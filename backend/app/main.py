"""Antenna ML Research Hub - FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import datasets, ml_models, visualizations, publications, knowledge_base, quick_actions

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Integrated research assistant for antenna ML workflows: "
                "simulation data import, ML model training, publication-quality "
                "visualization, and paper formatting.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for exports
exports_dir = Path(settings.STORAGE_PATH) / settings.EXPORT_DIR
exports_dir.mkdir(parents=True, exist_ok=True)
app.mount("/exports", StaticFiles(directory=str(exports_dir)), name="exports")

# Routes
app.include_router(datasets.router, prefix="/api")
app.include_router(ml_models.router, prefix="/api")
app.include_router(visualizations.router, prefix="/api")
app.include_router(publications.router, prefix="/api")
app.include_router(knowledge_base.router, prefix="/api")
app.include_router(quick_actions.router, prefix="/api")


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/dashboard")
def dashboard():
    """Dashboard summary statistics."""
    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal
    from app.models.dataset import Dataset
    from app.models.ml_model import MLModel
    from app.models.antenna_design import AntennaDesign
    from app.models.publication import Publication

    db = SessionLocal()
    try:
        total_datasets = db.query(Dataset).count()
        total_models = db.query(MLModel).count()
        total_designs = db.query(AntennaDesign).count()
        total_publications = db.query(Publication).count()

        # Best model
        best_model = db.query(MLModel).filter(
            MLModel.r2_score.isnot(None)
        ).order_by(MLModel.r2_score.desc()).first()

        # Recent datasets
        recent_datasets = db.query(Dataset).order_by(
            Dataset.created_at.desc()
        ).limit(5).all()

        # Active papers
        active_papers = db.query(Publication).filter(
            Publication.status.in_(["draft", "submitted", "revision"])
        ).count()

        return {
            "stats": {
                "total_datasets": total_datasets,
                "total_models": total_models,
                "total_designs": total_designs,
                "total_publications": total_publications,
                "active_papers": active_papers,
                "best_r2": best_model.r2_score if best_model else None,
                "best_model_name": best_model.name if best_model else None,
            },
            "recent_datasets": [
                {
                    "id": d.id,
                    "name": d.name,
                    "source": d.source,
                    "frequency_band": d.frequency_band,
                    "created_at": d.created_at.isoformat() if d.created_at else None,
                }
                for d in recent_datasets
            ],
        }
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "healthy"}
