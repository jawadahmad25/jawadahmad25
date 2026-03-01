from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class PublicationCreate(BaseModel):
    title: str
    journal: Optional[str] = None
    status: str = "draft"
    abstract: Optional[str] = None
    dataset_ids: list[int] = []
    model_ids: list[int] = []
    design_ids: list[int] = []
    tags: list[str] = []
    notes: Optional[str] = None


class PublicationResponse(BaseModel):
    id: int
    title: str
    journal: Optional[str]
    status: str
    abstract: Optional[str]
    highlights: Optional[list[str]]
    dataset_ids: list[int]
    model_ids: list[int]
    design_ids: list[int]
    tags: list[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class HighlightsRequest(BaseModel):
    abstract: str
    num_highlights: int = 5
    max_chars: int = 85


class HighlightsResponse(BaseModel):
    highlights: list[str]
    latex_formatted: str


class LatexTableRequest(BaseModel):
    data: Optional[list[dict]] = None
    csv_text: Optional[str] = None
    caption: str = "Table Caption"
    label: str = "tab:results"
    font_size: str = "normalsize"  # normalsize, small, footnotesize, scriptsize
    orientation: str = "portrait"  # portrait, landscape
    column_format: Optional[str] = None
    bold_header: bool = True


class LatexTableResponse(BaseModel):
    latex_code: str
    num_rows: int
    num_cols: int
    preview_text: str


class CitationCreate(BaseModel):
    bibtex: str
    publication_id: Optional[int] = None
    tags: list[str] = []


class CitationResponse(BaseModel):
    id: int
    title: Optional[str]
    authors: Optional[str]
    year: Optional[int]
    journal: Optional[str]
    doi: Optional[str]
    bibtex: str
    formatted_ieee: Optional[str]
    formatted_elsevier: Optional[str]
    tags: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
