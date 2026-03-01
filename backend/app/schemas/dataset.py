from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    frequency_band: Optional[str] = None
    antenna_type: Optional[str] = None
    source: str = "simulation"
    substrate: Optional[str] = None
    tags: list[str] = []
    notes: Optional[str] = None


class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency_band: Optional[str] = None
    antenna_type: Optional[str] = None
    substrate: Optional[str] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None


class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    file_path: str
    original_filename: str
    file_format: str
    frequency_band: Optional[str]
    antenna_type: Optional[str]
    source: str
    substrate: Optional[str]
    freq_min: Optional[float]
    freq_max: Optional[float]
    freq_step: Optional[float]
    num_points: Optional[int]
    columns: Optional[list[str]]
    tags: list[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DatasetListResponse(BaseModel):
    datasets: list[DatasetResponse]
    total: int


class AlignmentRequest(BaseModel):
    reference_dataset_id: Optional[int] = None
    target_dataset_id: Optional[int] = None
    interpolation_method: str = Field(default="cubic", pattern="^(linear|cubic|quadratic)$")
    freq_column: str = "frequency"
    value_columns: Optional[list[str]] = None
    output_name: Optional[str] = None


class AlignmentResponse(BaseModel):
    aligned_file_path: str
    reference_points: int
    target_points_original: int
    target_points_aligned: int
    freq_min: float
    freq_max: float
    freq_step: float
    preview_data: Optional[dict] = None


class SyntheticDataRequest(BaseModel):
    base_dataset_id: int
    base_frequency_ghz: float
    target_frequency_ghz: float
    scaling_method: str = "electromagnetic"
    output_name: Optional[str] = None


class SyntheticDataResponse(BaseModel):
    dataset_id: int
    file_path: str
    base_frequency_ghz: float
    target_frequency_ghz: float
    scaling_factor: float
    num_points: int
