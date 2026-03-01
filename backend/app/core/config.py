from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "Antenna ML Research Hub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://antenna_ml:antenna_ml_dev@localhost:5432/antenna_ml_hub"

    # Storage
    STORAGE_PATH: str = str(Path(__file__).parent.parent.parent.parent / "storage")
    DATASET_DIR: str = "datasets"
    MODEL_DIR: str = "models"
    EXPORT_DIR: str = "exports"

    # ML defaults
    ML_TEST_SIZE: float = 0.2
    ML_RANDOM_STATE: int = 42
    NN_DEFAULT_EPOCHS: int = 500
    NN_DEFAULT_BATCH_SIZE: int = 32

    # Figure defaults (IEEE)
    FIG_WIDTH_INCHES: float = 3.5
    FIG_HEIGHT_INCHES: float = 2.625
    FIG_DPI: int = 600
    FIG_FONT_FAMILY: str = "Times New Roman"
    FIG_FONT_SIZE: int = 10

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
