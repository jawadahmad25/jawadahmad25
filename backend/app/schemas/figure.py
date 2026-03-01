from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Any


class FigureRequest(BaseModel):
    plot_type: str  # s_parameter, radiation_pattern, gain_vs_angle, ml_comparison, scatter, rssi_distance, rain_attenuation, channel_capacity
    dataset_id: Optional[int] = None
    data: Optional[dict[str, Any]] = None

    # Plot configuration
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    x_column: Optional[str] = None
    y_columns: Optional[list[str]] = None

    # Style
    style: str = "ieee"  # ieee, elsevier, custom
    width_inches: float = 3.5
    height_inches: float = 2.625
    dpi: int = 600
    font_size: int = 10
    line_width: float = 1.5
    show_grid: bool = True
    grid_alpha: float = 0.3
    colors: Optional[list[str]] = None
    markers: Optional[list[str]] = None
    legend_labels: Optional[list[str]] = None
    legend_position: str = "best"

    # Export
    export_format: str = "png"  # png, pdf, eps, svg


class FigureResponse(BaseModel):
    id: Optional[int] = None
    file_path: str
    plot_type: str
    format: str
    preview_url: str

    model_config = {"from_attributes": True}
