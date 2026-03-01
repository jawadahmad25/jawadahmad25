from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON

from app.core.database import Base


class AntennaDesign(Base):
    __tablename__ = "antenna_designs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Geometry
    geometry_params = Column(JSON, nullable=True)
    dimensions_mm = Column(JSON, nullable=True)

    # Performance
    performance = Column(JSON, nullable=True)
    s11_min_db = Column(Float, nullable=True)
    peak_gain_dbi = Column(Float, nullable=True)
    bandwidth_mhz = Column(Float, nullable=True)

    # Classification
    frequency_band = Column(String(50), nullable=True)
    antenna_type = Column(String(100), nullable=True)
    substrate = Column(String(100), nullable=True)
    application = Column(String(100), nullable=True)

    # Linked resources
    dataset_ids = Column(JSON, default=list)
    model_ids = Column(JSON, default=list)
    paper_ids = Column(JSON, default=list)
    file_paths = Column(JSON, default=list)

    tags = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
