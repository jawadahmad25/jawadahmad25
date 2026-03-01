from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TrainingRequest(BaseModel):
    dataset_id: int
    target_variable: str
    feature_columns: list[str]
    model_types: list[str]  # ["linear_regression", "random_forest", ...]
    test_size: float = 0.2
    hyperparameters: Optional[dict[str, dict]] = None
    name_prefix: Optional[str] = None


class ModelResult(BaseModel):
    model_type: str
    mse: float
    rmse: float
    mae: float
    r2_score: float
    training_duration_seconds: float
    feature_importance: Optional[dict[str, float]] = None
    model_id: int


class TrainingResponse(BaseModel):
    results: list[ModelResult]
    dataset_name: str
    target_variable: str
    num_training_samples: int
    num_test_samples: int


class PredictionRequest(BaseModel):
    model_id: int
    input_features: dict[str, float]


class PredictionResponse(BaseModel):
    prediction: float
    model_type: str
    model_name: str
    confidence_interval: Optional[dict[str, float]] = None
    input_features: dict[str, float]


class MLModelResponse(BaseModel):
    id: int
    name: str
    model_type: str
    dataset_id: int
    target_variable: str
    feature_columns: list[str]
    hyperparameters: Optional[dict]
    mse: Optional[float]
    rmse: Optional[float]
    mae: Optional[float]
    r2_score: Optional[float]
    training_duration_seconds: Optional[float]
    feature_importance: Optional[dict]
    training_history: Optional[dict]
    notes: Optional[str]
    tags: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MLModelListResponse(BaseModel):
    models: list[MLModelResponse]
    total: int
