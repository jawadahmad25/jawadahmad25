from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Figure(Base):
    __tablename__ = "figures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    plot_type = Column(String(50), nullable=False)  # s_parameter, radiation_pattern, gain_vs_angle, etc.
    file_path = Column(Text, nullable=True)

    # Configuration
    config = Column(JSON, nullable=True)  # Plot configuration (colors, markers, labels, etc.)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True)

    # Export info
    format = Column(String(10), nullable=True)  # png, pdf, eps
    width_inches = Column(String(10), nullable=True)
    dpi = Column(Integer, nullable=True)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("Dataset", back_populates="figures")
