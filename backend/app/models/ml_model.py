from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ModelType(str, enum.Enum):
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    SVR = "svr"
    NEURAL_NETWORK = "neural_network"


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    model_type = Column(SQLEnum(ModelType), nullable=False)
    file_path = Column(Text, nullable=False)

    # Training config
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    target_variable = Column(String(100), nullable=False)
    feature_columns = Column(JSON, nullable=False)
    hyperparameters = Column(JSON, nullable=True)

    # Performance metrics
    mse = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    r2_score = Column(Float, nullable=True)
    performance_metrics = Column(JSON, nullable=True)

    # Training details
    training_duration_seconds = Column(Float, nullable=True)
    feature_importance = Column(JSON, nullable=True)
    training_history = Column(JSON, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    dataset = relationship("Dataset", back_populates="ml_models")

    def __repr__(self) -> str:
        return f"<MLModel(id={self.id}, type='{self.model_type}', R²={self.r2_score})>"
