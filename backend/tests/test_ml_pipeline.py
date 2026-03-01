"""Tests for ML pipeline."""
import pytest
import tempfile
import shutil
import numpy as np
import pandas as pd

from app.services.ml_pipeline import MLPipeline


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture
def pipeline(temp_storage):
    return MLPipeline(storage_path=temp_storage)


@pytest.fixture
def sample_data():
    """Generate synthetic antenna parameter data."""
    np.random.seed(42)
    n = 200

    # Simulate antenna parameters
    patch_length = np.random.uniform(3.5, 5.0, n)
    patch_width = np.random.uniform(2.5, 4.0, n)
    substrate_height = np.random.uniform(0.5, 1.5, n)
    epsilon_r = np.random.choice([2.2, 3.5, 4.4, 6.15], n)

    # S11 depends on geometry (simplified physics model)
    s11 = -20 * patch_length / 4.5 - 5 * substrate_height + 3 * epsilon_r + np.random.normal(0, 1, n)

    return pd.DataFrame({
        "patch_length": patch_length,
        "patch_width": patch_width,
        "substrate_height": substrate_height,
        "epsilon_r": epsilon_r,
        "s11_db": s11,
    })


class TestMLPipeline:
    def test_train_linear_regression(self, pipeline, sample_data):
        results = pipeline.train_all(
            sample_data,
            target_variable="s11_db",
            feature_columns=["patch_length", "patch_width", "substrate_height", "epsilon_r"],
            model_types=["linear_regression"],
            name_prefix="test_lr",
        )
        assert len(results) == 1
        assert results[0]["model_type"] == "linear_regression"
        assert results[0]["r2_score"] > 0.5  # Should have decent fit
        assert results[0]["mse"] >= 0
        assert results[0]["rmse"] >= 0
        assert results[0]["mae"] >= 0

    def test_train_random_forest(self, pipeline, sample_data):
        results = pipeline.train_all(
            sample_data,
            target_variable="s11_db",
            feature_columns=["patch_length", "patch_width", "substrate_height", "epsilon_r"],
            model_types=["random_forest"],
            name_prefix="test_rf",
        )
        assert len(results) == 1
        assert results[0]["model_type"] == "random_forest"
        assert results[0]["r2_score"] > 0.7
        assert results[0]["feature_importance"] is not None
        assert "patch_length" in results[0]["feature_importance"]

    def test_train_multiple_models(self, pipeline, sample_data):
        model_types = ["linear_regression", "random_forest", "gradient_boosting", "svr"]
        results = pipeline.train_all(
            sample_data,
            target_variable="s11_db",
            feature_columns=["patch_length", "patch_width", "substrate_height", "epsilon_r"],
            model_types=model_types,
            name_prefix="test_multi",
        )
        assert len(results) == 4
        for r in results:
            assert r["model_type"] in model_types
            assert r["r2_score"] is not None
            assert r["training_duration_seconds"] > 0

    def test_train_neural_network(self, pipeline, sample_data):
        results = pipeline.train_all(
            sample_data,
            target_variable="s11_db",
            feature_columns=["patch_length", "patch_width", "substrate_height", "epsilon_r"],
            model_types=["neural_network"],
            hyperparameters={
                "neural_network": {"epochs": 50, "hidden_layers": [32, 16]}
            },
            name_prefix="test_nn",
        )
        assert len(results) == 1
        assert results[0]["model_type"] == "neural_network"
        assert results[0]["training_history"] is not None

    def test_prediction(self, pipeline, sample_data):
        # Train a model first
        results = pipeline.train_all(
            sample_data,
            target_variable="s11_db",
            feature_columns=["patch_length", "patch_width", "substrate_height", "epsilon_r"],
            model_types=["random_forest"],
            name_prefix="test_pred",
        )

        # Make prediction
        pred = pipeline.predict(
            model_path=results[0]["model_path"],
            model_type="random_forest",
            scaler_path=results[0]["scaler_path"],
            input_features={
                "patch_length": 4.2,
                "patch_width": 3.5,
                "substrate_height": 0.787,
                "epsilon_r": 2.2,
            },
            feature_columns=["patch_length", "patch_width", "substrate_height", "epsilon_r"],
        )
        assert "prediction" in pred
        assert isinstance(pred["prediction"], float)

    def test_model_files_saved(self, pipeline, sample_data, temp_storage):
        from pathlib import Path

        pipeline.train_all(
            sample_data,
            target_variable="s11_db",
            feature_columns=["patch_length", "patch_width"],
            model_types=["random_forest"],
            name_prefix="test_save",
        )

        # Check files exist
        model_files = list(Path(temp_storage).glob("*.pkl"))
        assert len(model_files) >= 2  # model + scaler
