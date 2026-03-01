"""Knowledge base and antenna design library API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.antenna_design import AntennaDesign
from app.models.dataset import Dataset
from app.models.ml_model import MLModel
from app.models.publication import Publication
from app.schemas.antenna_design import AntennaDesignCreate, AntennaDesignResponse

router = APIRouter(prefix="/knowledge-base", tags=["knowledge_base"])


# ── Antenna Design Library ──

@router.post("/designs", response_model=AntennaDesignResponse)
def create_design(
    design: AntennaDesignCreate,
    db: Session = Depends(get_db),
):
    """Create a new antenna design entry."""
    db_design = AntennaDesign(
        name=design.name,
        description=design.description,
        geometry_params=design.geometry_params,
        dimensions_mm=design.dimensions_mm,
        performance=design.performance,
        s11_min_db=design.s11_min_db,
        peak_gain_dbi=design.peak_gain_dbi,
        bandwidth_mhz=design.bandwidth_mhz,
        frequency_band=design.frequency_band,
        antenna_type=design.antenna_type,
        substrate=design.substrate,
        application=design.application,
        dataset_ids=design.dataset_ids,
        model_ids=design.model_ids,
        paper_ids=design.paper_ids,
        tags=design.tags,
        notes=design.notes,
    )
    db.add(db_design)
    db.commit()
    db.refresh(db_design)
    return db_design


@router.get("/designs", response_model=list[AntennaDesignResponse])
def list_designs(
    search: str = None,
    frequency_band: str = None,
    antenna_type: str = None,
    substrate: str = None,
    application: str = None,
    min_gain: float = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Search and list antenna designs."""
    query = db.query(AntennaDesign)

    if search:
        query = query.filter(
            or_(
                AntennaDesign.name.ilike(f"%{search}%"),
                AntennaDesign.description.ilike(f"%{search}%"),
                AntennaDesign.notes.ilike(f"%{search}%"),
            )
        )
    if frequency_band:
        query = query.filter(AntennaDesign.frequency_band.ilike(f"%{frequency_band}%"))
    if antenna_type:
        query = query.filter(AntennaDesign.antenna_type.ilike(f"%{antenna_type}%"))
    if substrate:
        query = query.filter(AntennaDesign.substrate.ilike(f"%{substrate}%"))
    if application:
        query = query.filter(AntennaDesign.application.ilike(f"%{application}%"))
    if min_gain is not None:
        query = query.filter(AntennaDesign.peak_gain_dbi >= min_gain)

    return query.order_by(AntennaDesign.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/designs/{design_id}", response_model=AntennaDesignResponse)
def get_design(design_id: int, db: Session = Depends(get_db)):
    """Get a single antenna design."""
    design = db.query(AntennaDesign).filter(AntennaDesign.id == design_id).first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design


@router.put("/designs/{design_id}", response_model=AntennaDesignResponse)
def update_design(
    design_id: int,
    update: AntennaDesignCreate,
    db: Session = Depends(get_db),
):
    """Update an antenna design."""
    design = db.query(AntennaDesign).filter(AntennaDesign.id == design_id).first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(design, field, value)

    db.commit()
    db.refresh(design)
    return design


# ── Cross-Reference System ──

@router.get("/cross-reference/{resource_type}/{resource_id}")
def get_cross_references(
    resource_type: str,
    resource_id: int,
    db: Session = Depends(get_db),
):
    """Get all resources linked to a specific item."""
    result = {"resource_type": resource_type, "resource_id": resource_id, "linked": {}}

    if resource_type == "dataset":
        dataset = db.query(Dataset).filter(Dataset.id == resource_id).first()
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Find models trained on this dataset
        models = db.query(MLModel).filter(MLModel.dataset_id == resource_id).all()
        result["linked"]["models"] = [
            {"id": m.id, "name": m.name, "type": m.model_type, "r2": m.r2_score}
            for m in models
        ]

        # Find designs using this dataset
        designs = db.query(AntennaDesign).all()
        linked_designs = [d for d in designs if resource_id in (d.dataset_ids or [])]
        result["linked"]["designs"] = [
            {"id": d.id, "name": d.name, "frequency_band": d.frequency_band}
            for d in linked_designs
        ]

        # Find publications using this dataset
        pubs = db.query(Publication).all()
        linked_pubs = [p for p in pubs if resource_id in (p.dataset_ids or [])]
        result["linked"]["publications"] = [
            {"id": p.id, "title": p.title, "status": p.status}
            for p in linked_pubs
        ]

    elif resource_type == "model":
        model = db.query(MLModel).filter(MLModel.id == resource_id).first()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        result["linked"]["dataset"] = {
            "id": model.dataset_id,
            "name": model.dataset.name if model.dataset else None,
        }

    elif resource_type == "design":
        design = db.query(AntennaDesign).filter(AntennaDesign.id == resource_id).first()
        if not design:
            raise HTTPException(status_code=404, detail="Design not found")

        if design.dataset_ids:
            datasets = db.query(Dataset).filter(Dataset.id.in_(design.dataset_ids)).all()
            result["linked"]["datasets"] = [
                {"id": d.id, "name": d.name} for d in datasets
            ]
        if design.model_ids:
            models = db.query(MLModel).filter(MLModel.id.in_(design.model_ids)).all()
            result["linked"]["models"] = [
                {"id": m.id, "name": m.name, "r2": m.r2_score} for m in models
            ]
        if design.paper_ids:
            pubs = db.query(Publication).filter(Publication.id.in_(design.paper_ids)).all()
            result["linked"]["publications"] = [
                {"id": p.id, "title": p.title} for p in pubs
            ]

    return result


# ── Insights ──

@router.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    """Get research insights and statistics."""
    datasets = db.query(Dataset).all()
    models = db.query(MLModel).all()
    designs = db.query(AntennaDesign).all()
    publications = db.query(Publication).all()

    # Best models
    best_models = sorted(
        [m for m in models if m.r2_score is not None],
        key=lambda m: m.r2_score,
        reverse=True,
    )[:5]

    # Frequency band distribution
    freq_bands = {}
    for d in datasets:
        band = d.frequency_band or "Unknown"
        freq_bands[band] = freq_bands.get(band, 0) + 1

    # Substrate usage
    substrates = {}
    for d in designs:
        sub = d.substrate or "Unknown"
        substrates[sub] = substrates.get(sub, 0) + 1

    # Average performance by frequency band
    band_performance = {}
    for d in designs:
        band = d.frequency_band or "Unknown"
        if band not in band_performance:
            band_performance[band] = {"gains": [], "bandwidths": [], "s11_mins": []}
        if d.peak_gain_dbi is not None:
            band_performance[band]["gains"].append(d.peak_gain_dbi)
        if d.bandwidth_mhz is not None:
            band_performance[band]["bandwidths"].append(d.bandwidth_mhz)
        if d.s11_min_db is not None:
            band_performance[band]["s11_mins"].append(d.s11_min_db)

    import numpy as np
    band_avg = {}
    for band, metrics in band_performance.items():
        band_avg[band] = {
            "avg_gain_dbi": float(np.mean(metrics["gains"])) if metrics["gains"] else None,
            "avg_bandwidth_mhz": float(np.mean(metrics["bandwidths"])) if metrics["bandwidths"] else None,
            "avg_s11_min_db": float(np.mean(metrics["s11_mins"])) if metrics["s11_mins"] else None,
        }

    return {
        "summary": {
            "total_datasets": len(datasets),
            "total_models": len(models),
            "total_designs": len(designs),
            "total_publications": len(publications),
            "best_r2": best_models[0].r2_score if best_models else None,
        },
        "best_models": [
            {"id": m.id, "name": m.name, "type": m.model_type, "r2": m.r2_score}
            for m in best_models
        ],
        "frequency_band_distribution": freq_bands,
        "substrate_usage": substrates,
        "performance_by_band": band_avg,
    }
