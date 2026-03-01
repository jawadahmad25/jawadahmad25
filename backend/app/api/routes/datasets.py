"""Dataset management API routes."""
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.dataset import Dataset, DataSourceType, FileFormat
from app.schemas.dataset import (
    DatasetCreate, DatasetUpdate, DatasetResponse, DatasetListResponse,
    AlignmentRequest, AlignmentResponse,
    SyntheticDataRequest, SyntheticDataResponse,
)
from app.services.data_parser import DataParser
from app.services.data_alignment import DataAlignmentEngine
from app.services.synthetic_data import SyntheticDataGenerator

router = APIRouter(prefix="/datasets", tags=["datasets"])
parser = DataParser()
alignment_engine = DataAlignmentEngine()
synthetic_gen = SyntheticDataGenerator()


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(None),
    frequency_band: str = Form(None),
    antenna_type: str = Form(None),
    source: str = Form("simulation"),
    substrate: str = Form(None),
    tags: str = Form("[]"),
    db: Session = Depends(get_db),
):
    """Upload and parse a dataset file."""
    # Save uploaded file
    storage_dir = Path(settings.STORAGE_PATH) / settings.DATASET_DIR
    storage_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid.uuid4())[:8]
    file_ext = Path(file.filename).suffix
    stored_filename = f"{file_id}_{file.filename}"
    file_path = storage_dir / stored_filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Parse file
    try:
        parsed = parser.parse(str(file_path))
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if parsed.get("data") is None:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=parsed.get("error", "No data found in file"))

    # Parse tags
    import json
    try:
        tag_list = json.loads(tags) if tags else []
    except json.JSONDecodeError:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    # Create dataset record
    dataset = Dataset(
        name=name,
        description=description,
        file_path=str(file_path),
        original_filename=file.filename,
        file_format=parsed.get("file_format", "generic_csv"),
        frequency_band=frequency_band,
        antenna_type=antenna_type,
        source=source,
        substrate=substrate,
        freq_min=parsed.get("freq_min"),
        freq_max=parsed.get("freq_max"),
        freq_step=parsed.get("freq_step"),
        num_points=parsed.get("num_points"),
        columns=parsed.get("columns"),
        tags=tag_list,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


@router.get("/", response_model=DatasetListResponse)
def list_datasets(
    search: str = None,
    frequency_band: str = None,
    source: str = None,
    antenna_type: str = None,
    substrate: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List datasets with optional filtering."""
    query = db.query(Dataset)

    if search:
        query = query.filter(Dataset.name.ilike(f"%{search}%"))
    if frequency_band:
        query = query.filter(Dataset.frequency_band == frequency_band)
    if source:
        query = query.filter(Dataset.source == source)
    if antenna_type:
        query = query.filter(Dataset.antenna_type.ilike(f"%{antenna_type}%"))
    if substrate:
        query = query.filter(Dataset.substrate.ilike(f"%{substrate}%"))

    total = query.count()
    datasets = query.order_by(Dataset.created_at.desc()).offset(skip).limit(limit).all()
    return DatasetListResponse(datasets=datasets, total=total)


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Get a single dataset by ID."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.put("/{dataset_id}", response_model=DatasetResponse)
def update_dataset(
    dataset_id: int,
    update: DatasetUpdate,
    db: Session = Depends(get_db),
):
    """Update dataset metadata."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(dataset, field, value)

    db.commit()
    db.refresh(dataset)
    return dataset


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Delete file
    Path(dataset.file_path).unlink(missing_ok=True)

    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted"}


@router.get("/{dataset_id}/preview")
def preview_dataset(dataset_id: int, rows: int = 50, db: Session = Depends(get_db)):
    """Get a preview of dataset contents."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    parsed = parser.parse(dataset.file_path, dataset.file_format)
    if parsed.get("data") is None:
        raise HTTPException(status_code=500, detail="Could not read dataset")

    df = parsed["data"]
    preview = df.head(rows)

    return {
        "columns": list(df.columns),
        "data": preview.to_dict(orient="records"),
        "total_rows": len(df),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


@router.post("/align", response_model=AlignmentResponse)
async def align_datasets(
    reference_file: UploadFile = File(None),
    target_file: UploadFile = File(None),
    reference_dataset_id: int = Form(None),
    target_dataset_id: int = Form(None),
    interpolation_method: str = Form("cubic"),
    output_name: str = Form(None),
    db: Session = Depends(get_db),
):
    """Align two datasets onto a common frequency grid."""
    storage_dir = Path(settings.STORAGE_PATH) / settings.DATASET_DIR
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Get reference data
    if reference_dataset_id:
        ref_ds = db.query(Dataset).filter(Dataset.id == reference_dataset_id).first()
        if not ref_ds:
            raise HTTPException(status_code=404, detail="Reference dataset not found")
        ref_parsed = parser.parse(ref_ds.file_path, ref_ds.file_format)
    elif reference_file:
        temp_ref = storage_dir / f"temp_ref_{reference_file.filename}"
        with open(temp_ref, "wb") as f:
            shutil.copyfileobj(reference_file.file, f)
        ref_parsed = parser.parse(str(temp_ref))
    else:
        raise HTTPException(status_code=400, detail="Provide reference_dataset_id or reference_file")

    # Get target data
    if target_dataset_id:
        target_ds = db.query(Dataset).filter(Dataset.id == target_dataset_id).first()
        if not target_ds:
            raise HTTPException(status_code=404, detail="Target dataset not found")
        target_parsed = parser.parse(target_ds.file_path, target_ds.file_format)
    elif target_file:
        temp_target = storage_dir / f"temp_target_{target_file.filename}"
        with open(temp_target, "wb") as f:
            shutil.copyfileobj(target_file.file, f)
        target_parsed = parser.parse(str(temp_target))
    else:
        raise HTTPException(status_code=400, detail="Provide target_dataset_id or target_file")

    if ref_parsed.get("data") is None or target_parsed.get("data") is None:
        raise HTTPException(status_code=400, detail="Could not parse one or both files")

    # Align
    output_name = output_name or f"aligned_{uuid.uuid4().hex[:8]}"
    output_path = str(storage_dir / f"{output_name}.csv")

    try:
        result = alignment_engine.align(
            ref_parsed["data"],
            target_parsed["data"],
            ref_freq_col=ref_parsed.get("freq_column", "Frequency_GHz"),
            target_freq_col=target_parsed.get("freq_column", "Frequency_GHz"),
            method=interpolation_method,
            output_path=output_path,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    stats = result["stats"]
    return AlignmentResponse(
        aligned_file_path=output_path,
        reference_points=stats["reference"]["num_points"],
        target_points_original=stats["target"]["num_points"],
        target_points_aligned=stats["aligned"]["num_points"],
        freq_min=stats["aligned"]["freq_min"],
        freq_max=stats["aligned"]["freq_max"],
        freq_step=stats["aligned"]["freq_step"],
        preview_data=result["preview"],
    )


@router.post("/synthetic", response_model=SyntheticDataResponse)
def generate_synthetic_data(
    request: SyntheticDataRequest,
    db: Session = Depends(get_db),
):
    """Generate synthetic dataset using electromagnetic scaling."""
    base_ds = db.query(Dataset).filter(Dataset.id == request.base_dataset_id).first()
    if not base_ds:
        raise HTTPException(status_code=404, detail="Base dataset not found")

    parsed = parser.parse(base_ds.file_path, base_ds.file_format)
    if parsed.get("data") is None:
        raise HTTPException(status_code=500, detail="Could not read base dataset")

    storage_dir = Path(settings.STORAGE_PATH) / settings.DATASET_DIR
    output_name = request.output_name or f"synthetic_{request.target_frequency_ghz}GHz_{uuid.uuid4().hex[:8]}"
    output_path = str(storage_dir / f"{output_name}.csv")

    freq_col = parsed.get("freq_column", "Frequency_GHz")
    result = synthetic_gen.generate(
        parsed["data"],
        request.base_frequency_ghz,
        request.target_frequency_ghz,
        freq_column=freq_col,
        scaling_method=request.scaling_method,
        output_path=output_path,
    )

    # Save as new dataset
    new_dataset = Dataset(
        name=output_name,
        description=f"Synthetic data scaled from {request.base_frequency_ghz} to {request.target_frequency_ghz} GHz",
        file_path=output_path,
        original_filename=f"{output_name}.csv",
        file_format="generic_csv",
        frequency_band=f"{request.target_frequency_ghz} GHz",
        source="synthetic",
        freq_min=result["data"]["Frequency_GHz"].min() if "Frequency_GHz" in result["data"].columns else None,
        freq_max=result["data"]["Frequency_GHz"].max() if "Frequency_GHz" in result["data"].columns else None,
        num_points=result["num_points"],
        columns=list(result["data"].columns),
        tags=["synthetic", f"scaled_from_{request.base_frequency_ghz}GHz"],
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)

    return SyntheticDataResponse(
        dataset_id=new_dataset.id,
        file_path=output_path,
        base_frequency_ghz=request.base_frequency_ghz,
        target_frequency_ghz=request.target_frequency_ghz,
        scaling_factor=result["scaling_factor"],
        num_points=result["num_points"],
    )
