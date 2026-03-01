"""Visualization and figure generation API routes."""
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.dataset import Dataset
from app.models.figure import Figure
from app.schemas.figure import FigureRequest, FigureResponse
from app.services.data_parser import DataParser
from app.services.figure_generator import FigureGenerator

router = APIRouter(prefix="/visualizations", tags=["visualizations"])
parser = DataParser()
fig_gen = FigureGenerator()


@router.post("/generate", response_model=FigureResponse)
def generate_figure(
    request: FigureRequest,
    db: Session = Depends(get_db),
):
    """Generate a publication-quality figure."""
    data = request.data or {}

    # If dataset_id provided, load data from dataset
    if request.dataset_id:
        dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        parsed = parser.parse(dataset.file_path, dataset.file_format)
        if parsed.get("data") is None:
            raise HTTPException(status_code=500, detail="Could not read dataset")

        df = parsed["data"]

        # Auto-build traces from dataframe
        freq_col = parsed.get("freq_column", df.columns[0])
        y_columns = request.y_columns or [c for c in df.columns if c != freq_col]

        data["frequency"] = df[freq_col].tolist()
        data["traces"] = {col: df[col].tolist() for col in y_columns if col in df.columns}

    if not data:
        raise HTTPException(status_code=400, detail="No data provided")

    # Apply labels
    if request.title:
        data["title"] = request.title
    if request.x_label:
        data["x_label"] = request.x_label
    if request.y_label:
        data["y_label"] = request.y_label
    if request.colors:
        data["colors"] = request.colors
    if request.markers:
        data["markers"] = request.markers
    if request.legend_labels:
        data["labels"] = request.legend_labels
    data["legend_position"] = request.legend_position

    # Generate figure
    export_dir = Path(settings.STORAGE_PATH) / settings.EXPORT_DIR
    export_dir.mkdir(parents=True, exist_ok=True)
    fig_id = uuid.uuid4().hex[:8]
    output_path = str(export_dir / f"fig_{fig_id}.{request.export_format}")

    config = {
        "width_inches": request.width_inches,
        "height_inches": request.height_inches,
        "dpi": request.dpi,
        "font_size": request.font_size,
        "line_width": request.line_width,
        "grid": request.show_grid,
        "grid_alpha": request.grid_alpha,
    }

    try:
        result = fig_gen.generate(
            plot_type=request.plot_type,
            data=data,
            config=config,
            output_path=output_path,
            export_format=request.export_format,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save to DB
    figure = Figure(
        name=request.title or f"{request.plot_type}_{fig_id}",
        plot_type=request.plot_type,
        file_path=output_path,
        config=config,
        dataset_id=request.dataset_id,
        format=request.export_format,
        width_inches=str(request.width_inches),
        dpi=request.dpi,
    )
    db.add(figure)
    db.commit()
    db.refresh(figure)

    return FigureResponse(
        id=figure.id,
        file_path=output_path,
        plot_type=request.plot_type,
        format=request.export_format,
        preview_url=f"/api/visualizations/{figure.id}/preview",
    )


@router.post("/generate/interactive")
def generate_interactive_figure(
    request: FigureRequest,
    db: Session = Depends(get_db),
):
    """Generate an interactive Plotly figure (JSON)."""
    data = request.data or {}

    if request.dataset_id:
        dataset = db.query(Dataset).filter(Dataset.id == request.dataset_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        parsed = parser.parse(dataset.file_path, dataset.file_format)
        if parsed.get("data") is None:
            raise HTTPException(status_code=500, detail="Could not read dataset")

        df = parsed["data"]
        freq_col = parsed.get("freq_column", df.columns[0])
        y_columns = request.y_columns or [c for c in df.columns if c != freq_col]

        data["frequency"] = df[freq_col].tolist()
        data["traces"] = {col: df[col].tolist() for col in y_columns if col in df.columns}

    if request.title:
        data["title"] = request.title
    if request.x_label:
        data["x_label"] = request.x_label
    if request.y_label:
        data["y_label"] = request.y_label

    result = fig_gen.generate_plotly(
        plot_type=request.plot_type,
        data=data,
    )

    return result


@router.get("/{figure_id}/preview")
def get_figure_preview(figure_id: int, db: Session = Depends(get_db)):
    """Get a figure file for preview."""
    figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")

    file_path = Path(figure.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Figure file not found")

    media_types = {
        "png": "image/png",
        "pdf": "application/pdf",
        "eps": "application/postscript",
        "svg": "image/svg+xml",
    }

    return FileResponse(
        path=str(file_path),
        media_type=media_types.get(figure.format, "application/octet-stream"),
    )


@router.get("/{figure_id}/download")
def download_figure(figure_id: int, db: Session = Depends(get_db)):
    """Download a figure file."""
    figure = db.query(Figure).filter(Figure.id == figure_id).first()
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")

    file_path = Path(figure.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Figure file not found")

    return FileResponse(
        path=str(file_path),
        filename=f"{figure.name}.{figure.format}",
        media_type="application/octet-stream",
    )
