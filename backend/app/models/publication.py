from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    journal = Column(String(255), nullable=True)
    status = Column(String(50), default="draft")  # draft, submitted, revision, accepted, published
    abstract = Column(Text, nullable=True)
    highlights = Column(JSON, nullable=True)

    # Linked resources
    dataset_ids = Column(JSON, default=list)
    model_ids = Column(JSON, default=list)
    design_ids = Column(JSON, default=list)

    tags = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    citations = relationship("Citation", back_populates="publication")


class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    publication_id = Column(Integer, ForeignKey("publications.id"), nullable=True)
    bibtex = Column(Text, nullable=False)
    title = Column(String(500), nullable=True)
    authors = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    journal = Column(String(255), nullable=True)
    doi = Column(String(255), nullable=True)
    formatted_ieee = Column(Text, nullable=True)
    formatted_elsevier = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    publication = relationship("Publication", back_populates="citations")
