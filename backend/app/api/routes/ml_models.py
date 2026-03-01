"""ML model training and prediction API routes."""
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.dataset import Dataset
from app.models.ml_model import MLModel
from app.schemas.ml_model import (
    TrainingRequest, TrainingResponse, ModelResult,
    PredictionRequest, PredictionResponse,
    MLModelResponse, MLModelListResponse,
)
from app.services.data_parser import DataParser
from app.services.ml_pipeline import MLPipeline

router = APIRouter(prefix="/models", tags=["ml_models"])
parser = DataParser()


def get_pipeline() -> MLPipeline:
    storage = str(Path(settings.STORAGE_PATH) / settings.MODEL_DIR)
    return MLPipeline(storage_path=storage)


@router.post("/train", response_model=TrainingResponse)
def train_models(
    request: TrainingRequest,
    db: Session = Depends(get_db),
):
    """Train multiple ML models on a dataset."""
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Parse data
    parsed = parser.parse(dataset.file_path, dataset.file_format)
    if parsed.get("data") is None:
        raise HTTPException(status_code=500, detail="Could not read dataset")

    df = parsed["data"]

    # Validate columns
    missing_features = [c for c in request.feature_columns if c not in df.columns]
    if missing_features:
        raise HTTPException(
            status_code=400,
            detail=f"Feature columns not found in dataset: {missing_features}. Available: {list(df.columns)}",
        )
    if request.target_variable not in df.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Target variable '{request.target_variable}' not found. Available: {list(df.columns)}",
        )

    # Drop rows with NaN in relevant columns
    relevant_cols = request.feature_columns + [request.target_variable]
    df_clean = df[relevant_cols].dropna()

    if len(df_clean) < 10:
        raise HTTPException(status_code=400, detail=f"Not enough valid data points ({len(df_clean)}). Need at least 10.")

    # Train
    pipeline = get_pipeline()
    name_prefix = request.name_prefix or f"ds{dataset.id}_{request.target_variable}"

    results = pipeline.train_all(
        df_clean,
        target_variable=request.target_variable,
        feature_columns=request.feature_columns,
        model_types=request.model_types,
        test_size=request.test_size,
        hyperparameters=request.hyperparameters,
        name_prefix=name_prefix,
    )

    # Save models to DB
    model_results = []
    for result in results:
        ml_model = MLModel(
            name=f"{name_prefix}_{result['model_type']}",
            model_type=result["model_type"],
            file_path=result["model_path"],
            dataset_id=dataset.id,
            target_variable=request.target_variable,
            feature_columns=request.feature_columns,
            hyperparameters=result["hyperparameters"],
            mse=result["mse"],
            rmse=result["rmse"],
            mae=result["mae"],
            r2_score=result["r2_score"],
            training_duration_seconds=result["training_duration_seconds"],
            feature_importance=result.get("feature_importance"),
            training_history=result.get("training_history"),
            performance_metrics={
                "mse": result["mse"],
                "rmse": result["rmse"],
                "mae": result["mae"],
                "r2_score": result["r2_score"],
            },
        )
        db.add(ml_model)
        db.flush()

        model_results.append(ModelResult(
            model_type=result["model_type"],
            mse=result["mse"],
            rmse=result["rmse"],
            mae=result["mae"],
            r2_score=result["r2_score"],
            training_duration_seconds=result["training_duration_seconds"],
            feature_importance=result.get("feature_importance"),
            model_id=ml_model.id,
        ))

    db.commit()

    # Compute splits
    from sklearn.model_selection import train_test_split
    num_total = len(df_clean)
    num_test = int(num_total * request.test_size)
    num_train = num_total - num_test

    return TrainingResponse(
        results=model_results,
        dataset_name=dataset.name,
        target_variable=request.target_variable,
        num_training_samples=num_train,
        num_test_samples=num_test,
    )


@router.get("/", response_model=MLModelListResponse)
def list_models(
    search: str = None,
    model_type: str = None,
    dataset_id: int = None,
    min_r2: float = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List trained models with optional filtering."""
    query = db.query(MLModel)

    if search:
        query = query.filter(MLModel.name.ilike(f"%{search}%"))
    if model_type:
        query = query.filter(MLModel.model_type == model_type)
    if dataset_id:
        query = query.filter(MLModel.dataset_id == dataset_id)
    if min_r2 is not None:
        query = query.filter(MLModel.r2_score >= min_r2)

    total = query.count()
    models = query.order_by(MLModel.created_at.desc()).offset(skip).limit(limit).all()
    return MLModelListResponse(models=models, total=total)


@router.get("/{model_id}", response_model=MLModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    """Get a single model by ID."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/predict", response_model=PredictionResponse)
def predict(
    request: PredictionRequest,
    db: Session = Depends(get_db),
):
    """Make a prediction using a trained model."""
    model = db.query(MLModel).filter(MLModel.id == request.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Find scaler path
    model_dir = str(Path(model.file_path).parent)
    name_parts = Path(model.file_path).stem.rsplit("_", 1)
    scaler_name = f"{'_'.join(name_parts[:-1])}_scaler.pkl" if len(name_parts) > 1 else "scaler.pkl"
    scaler_path = str(Path(model_dir) / scaler_name)

    if not Path(scaler_path).exists():
        # Try to find any scaler in the directory
        scaler_files = list(Path(model_dir).glob("*_scaler.pkl"))
        if scaler_files:
            scaler_path = str(scaler_files[0])
        else:
            raise HTTPException(status_code=500, detail="Scaler file not found")

    pipeline = get_pipeline()

    try:
        result = pipeline.predict(
            model_path=model.file_path,
            model_type=model.model_type,
            scaler_path=scaler_path,
            input_features=request.input_features,
            feature_columns=model.feature_columns,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    return PredictionResponse(
        prediction=result["prediction"],
        model_type=model.model_type,
        model_name=model.name,
        input_features=request.input_features,
    )


@router.delete("/{model_id}")
def delete_model(model_id: int, db: Session = Depends(get_db)):
    """Delete a trained model."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    Path(model.file_path).unlink(missing_ok=True)
    db.delete(model)
    db.commit()
    return {"message": "Model deleted"}
