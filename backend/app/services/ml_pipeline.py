"""
ML Pipeline for antenna parameter prediction.

Supports 5 model types:
1. Linear Regression
2. Random Forest
3. Gradient Boosting
4. Support Vector Regression (SVR)
5. Neural Network (PyTorch)
"""
import time
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# Default hyperparameters (proven good for antenna data)
DEFAULT_HYPERPARAMS = {
    "linear_regression": {},
    "random_forest": {
        "n_estimators": 200,
        "max_depth": 15,
        "min_samples_split": 5,
        "random_state": 42,
    },
    "gradient_boosting": {
        "n_estimators": 200,
        "learning_rate": 0.05,
        "max_depth": 5,
        "random_state": 42,
    },
    "svr": {
        "kernel": "rbf",
        "C": 100,
        "epsilon": 0.01,
        "gamma": "scale",
    },
    "neural_network": {
        "hidden_layers": [64, 32, 16],
        "activation": "relu",
        "epochs": 500,
        "batch_size": 32,
        "learning_rate": 0.001,
    },
}


class AntennaNet(nn.Module):
    """PyTorch neural network for antenna parameter prediction."""

    def __init__(self, input_dim: int, hidden_layers: list[int], activation: str = "relu"):
        super().__init__()
        layers = []
        prev_dim = input_dim

        activation_fn = {"relu": nn.ReLU, "tanh": nn.Tanh, "leaky_relu": nn.LeakyReLU}
        act_class = activation_fn.get(activation, nn.ReLU)

        for h_dim in hidden_layers:
            layers.append(nn.Linear(prev_dim, h_dim))
            layers.append(act_class())
            layers.append(nn.BatchNorm1d(h_dim))
            layers.append(nn.Dropout(0.1))
            prev_dim = h_dim

        layers.append(nn.Linear(prev_dim, 1))
        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class MLPipeline:
    """Orchestrates training, evaluation, and prediction for all model types."""

    def __init__(self, storage_path: str = "storage/models"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def train_all(
        self,
        df: pd.DataFrame,
        target_variable: str,
        feature_columns: list[str],
        model_types: list[str],
        test_size: float = 0.2,
        hyperparameters: Optional[dict[str, dict]] = None,
        name_prefix: str = "model",
    ) -> list[dict]:
        """Train multiple models and return comparison results."""
        # Prepare data
        X = df[feature_columns].values.astype(np.float64)
        y = df[target_variable].values.astype(np.float64)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Save scaler
        scaler_path = self.storage_path / f"{name_prefix}_scaler.pkl"
        joblib.dump(scaler, scaler_path)

        results = []
        for model_type in model_types:
            params = DEFAULT_HYPERPARAMS.get(model_type, {}).copy()
            if hyperparameters and model_type in hyperparameters:
                params.update(hyperparameters[model_type])

            result = self._train_single(
                model_type, X_train_scaled, X_test_scaled, y_train, y_test,
                params, feature_columns, name_prefix,
            )
            result["scaler_path"] = str(scaler_path)
            results.append(result)

        return results

    def _train_single(
        self,
        model_type: str,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        params: dict,
        feature_columns: list[str],
        name_prefix: str,
    ) -> dict:
        """Train a single model and return results."""
        start_time = time.time()

        if model_type == "neural_network":
            result = self._train_neural_network(X_train, X_test, y_train, y_test, params)
        else:
            result = self._train_sklearn(model_type, X_train, X_test, y_train, y_test, params)

        training_duration = time.time() - start_time

        # Save model
        model_filename = f"{name_prefix}_{model_type}"
        if model_type == "neural_network":
            model_path = self.storage_path / f"{model_filename}.pt"
            torch.save(result["model_object"].state_dict(), model_path)
            # Save architecture info
            arch_path = self.storage_path / f"{model_filename}_arch.json"
            arch_path.write_text(json.dumps({
                "input_dim": X_train.shape[1],
                "hidden_layers": params.get("hidden_layers", [64, 32, 16]),
                "activation": params.get("activation", "relu"),
            }))
        else:
            model_path = self.storage_path / f"{model_filename}.pkl"
            joblib.dump(result["model_object"], model_path)

        # Feature importance (for tree models)
        feature_importance = None
        if model_type in ("random_forest", "gradient_boosting"):
            importance = result["model_object"].feature_importances_
            feature_importance = {
                col: float(imp) for col, imp in zip(feature_columns, importance)
            }

        return {
            "model_type": model_type,
            "model_path": str(model_path),
            "hyperparameters": params,
            "mse": result["mse"],
            "rmse": result["rmse"],
            "mae": result["mae"],
            "r2_score": result["r2"],
            "training_duration_seconds": training_duration,
            "feature_importance": feature_importance,
            "training_history": result.get("training_history"),
            "predictions": {
                "y_test": y_test.tolist(),
                "y_pred": result["y_pred"].tolist(),
            },
        }

    def _train_sklearn(
        self,
        model_type: str,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        params: dict,
    ) -> dict:
        """Train a scikit-learn model."""
        model_classes = {
            "linear_regression": LinearRegression,
            "random_forest": RandomForestRegressor,
            "gradient_boosting": GradientBoostingRegressor,
            "svr": SVR,
        }

        model_class = model_classes[model_type]
        model = model_class(**params)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mse = float(mean_squared_error(y_test, y_pred))

        return {
            "model_object": model,
            "y_pred": y_pred,
            "mse": mse,
            "rmse": float(np.sqrt(mse)),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
        }

    def _train_neural_network(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray,
        params: dict,
    ) -> dict:
        """Train a PyTorch neural network."""
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        hidden_layers = params.get("hidden_layers", [64, 32, 16])
        activation = params.get("activation", "relu")
        epochs = params.get("epochs", 500)
        batch_size = params.get("batch_size", 32)
        lr = params.get("learning_rate", 0.001)

        model = AntennaNet(X_train.shape[1], hidden_layers, activation).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        criterion = nn.MSELoss()

        # Create data loaders
        X_train_t = torch.FloatTensor(X_train).to(device)
        y_train_t = torch.FloatTensor(y_train).reshape(-1, 1).to(device)
        X_test_t = torch.FloatTensor(X_test).to(device)

        dataset = TensorDataset(X_train_t, y_train_t)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Training loop
        history = {"train_loss": [], "val_loss": []}
        best_val_loss = float("inf")

        for epoch in range(epochs):
            model.train()
            epoch_loss = 0.0
            for X_batch, y_batch in loader:
                optimizer.zero_grad()
                pred = model(X_batch)
                loss = criterion(pred, y_batch)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()

            avg_train_loss = epoch_loss / len(loader)

            # Validation
            model.eval()
            with torch.no_grad():
                val_pred = model(X_test_t)
                y_test_t = torch.FloatTensor(y_test).reshape(-1, 1).to(device)
                val_loss = criterion(val_pred, y_test_t).item()

            # Record every 10th epoch for history
            if epoch % 10 == 0 or epoch == epochs - 1:
                history["train_loss"].append({"epoch": epoch, "loss": avg_train_loss})
                history["val_loss"].append({"epoch": epoch, "loss": val_loss})

            if val_loss < best_val_loss:
                best_val_loss = val_loss

        # Final predictions
        model.eval()
        with torch.no_grad():
            y_pred = model(X_test_t).cpu().numpy().flatten()

        mse = float(mean_squared_error(y_test, y_pred))

        return {
            "model_object": model,
            "y_pred": y_pred,
            "mse": mse,
            "rmse": float(np.sqrt(mse)),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
            "training_history": history,
        }

    def predict(
        self,
        model_path: str,
        model_type: str,
        scaler_path: str,
        input_features: dict[str, float],
        feature_columns: list[str],
    ) -> dict:
        """Make a prediction using a saved model."""
        # Load scaler
        scaler = joblib.load(scaler_path)

        # Prepare input
        X = np.array([[input_features.get(col, 0.0) for col in feature_columns]])
        X_scaled = scaler.transform(X)

        if model_type == "neural_network":
            arch_path = model_path.replace(".pt", "_arch.json")
            arch = json.loads(Path(arch_path).read_text())

            model = AntennaNet(arch["input_dim"], arch["hidden_layers"], arch["activation"])
            model.load_state_dict(torch.load(model_path, weights_only=True))
            model.eval()

            with torch.no_grad():
                X_tensor = torch.FloatTensor(X_scaled)
                prediction = model(X_tensor).item()
        else:
            model = joblib.load(model_path)
            prediction = float(model.predict(X_scaled)[0])

        return {
            "prediction": prediction,
            "model_type": model_type,
            "input_features": input_features,
        }
