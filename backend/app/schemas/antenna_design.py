from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AntennaDesignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    geometry_params: Optional[dict] = None
    dimensions_mm: Optional[dict] = None
    performance: Optional[dict] = None
    s11_min_db: Optional[float] = None
    peak_gain_dbi: Optional[float] = None
    bandwidth_mhz: Optional[float] = None
    frequency_band: Optional[str] = None
    antenna_type: Optional[str] = None
    substrate: Optional[str] = None
    application: Optional[str] = None
    dataset_ids: list[int] = []
    model_ids: list[int] = []
    paper_ids: list[int] = []
    tags: list[str] = []
    notes: Optional[str] = None


class AntennaDesignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    geometry_params: Optional[dict]
    dimensions_mm: Optional[dict]
    performance: Optional[dict]
    s11_min_db: Optional[float]
    peak_gain_dbi: Optional[float]
    bandwidth_mhz: Optional[float]
    frequency_band: Optional[str]
    antenna_type: Optional[str]
    substrate: Optional[str]
    application: Optional[str]
    dataset_ids: list[int]
    model_ids: list[int]
    paper_ids: list[int]
    file_paths: list[str]
    tags: list[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
