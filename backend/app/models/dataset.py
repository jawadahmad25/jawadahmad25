from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DataSourceType(str, enum.Enum):
    SIMULATION = "simulation"
    MEASUREMENT = "measurement"
    SYNTHETIC = "synthetic"


class FileFormat(str, enum.Enum):
    CST_TXT = "cst_txt"
    HFSS_CSV = "hfss_csv"
    VNA_S2P = "vna_s2p"
    VNA_CSV = "vna_csv"
    GENERIC_CSV = "generic_csv"


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(Text, nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_format = Column(SQLEnum(FileFormat), nullable=False)

    # Metadata
    frequency_band = Column(String(50), nullable=True)
    antenna_type = Column(String(100), nullable=True)
    source = Column(SQLEnum(DataSourceType), nullable=False)
    substrate = Column(String(100), nullable=True)

    # Frequency info
    freq_min = Column(Float, nullable=True)
    freq_max = Column(Float, nullable=True)
    freq_step = Column(Float, nullable=True)
    num_points = Column(Integer, nullable=True)

    # Columns detected
    columns = Column(JSON, nullable=True)
    tags = Column(JSON, default=list)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ml_models = relationship("MLModel", back_populates="dataset")
    figures = relationship("Figure", back_populates="dataset")

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, name='{self.name}', source='{self.source}')>"
