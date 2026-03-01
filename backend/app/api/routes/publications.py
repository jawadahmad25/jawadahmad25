"""Publication management API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.publication import Publication, Citation
from app.schemas.publication import (
    PublicationCreate, PublicationResponse,
    HighlightsRequest, HighlightsResponse,
    LatexTableRequest, LatexTableResponse,
    CitationCreate, CitationResponse,
)
from app.services.publication_tools import (
    LaTeXTableFormatter, HighlightsGenerator, CitationFormatter,
)

router = APIRouter(prefix="/publications", tags=["publications"])
latex_formatter = LaTeXTableFormatter()
highlights_gen = HighlightsGenerator()
citation_fmt = CitationFormatter()


# ── Publication CRUD ──

@router.post("/", response_model=PublicationResponse)
def create_publication(
    pub: PublicationCreate,
    db: Session = Depends(get_db),
):
    """Create a new publication record."""
    publication = Publication(
        title=pub.title,
        journal=pub.journal,
        status=pub.status,
        abstract=pub.abstract,
        dataset_ids=pub.dataset_ids,
        model_ids=pub.model_ids,
        design_ids=pub.design_ids,
        tags=pub.tags,
        notes=pub.notes,
    )
    db.add(publication)
    db.commit()
    db.refresh(publication)
    return publication


@router.get("/", response_model=list[PublicationResponse])
def list_publications(
    search: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List publications."""
    query = db.query(Publication)
    if search:
        query = query.filter(Publication.title.ilike(f"%{search}%"))
    if status:
        query = query.filter(Publication.status == status)

    return query.order_by(Publication.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{pub_id}", response_model=PublicationResponse)
def get_publication(pub_id: int, db: Session = Depends(get_db)):
    """Get a publication by ID."""
    pub = db.query(Publication).filter(Publication.id == pub_id).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    return pub


# ── LaTeX Table Formatter ──

@router.post("/latex-table", response_model=LatexTableResponse)
def generate_latex_table(request: LatexTableRequest):
    """Generate a LaTeX table from data."""
    if request.csv_text:
        result = latex_formatter.from_csv_text(
            request.csv_text,
            caption=request.caption,
            label=request.label,
            font_size=request.font_size,
            orientation=request.orientation,
            column_format=request.column_format,
            bold_header=request.bold_header,
        )
    elif request.data:
        result = latex_formatter.format_table(
            request.data,
            caption=request.caption,
            label=request.label,
            font_size=request.font_size,
            orientation=request.orientation,
            column_format=request.column_format,
            bold_header=request.bold_header,
        )
    else:
        raise HTTPException(status_code=400, detail="Provide 'data' or 'csv_text'")

    return LatexTableResponse(**result)


# ── Research Highlights ──

@router.post("/highlights", response_model=HighlightsResponse)
def generate_highlights(request: HighlightsRequest):
    """Generate Elsevier-style research highlights from an abstract."""
    result = highlights_gen.generate(
        abstract=request.abstract,
        num_highlights=request.num_highlights,
        max_chars=request.max_chars,
    )
    return HighlightsResponse(**result)


# ── Citation Manager ──

@router.post("/citations", response_model=CitationResponse)
def add_citation(
    request: CitationCreate,
    db: Session = Depends(get_db),
):
    """Parse and store a BibTeX citation."""
    parsed = citation_fmt.parse_bibtex(request.bibtex)

    formatted_ieee = citation_fmt.format_ieee(parsed)
    formatted_elsevier = citation_fmt.format_elsevier(parsed)

    citation = Citation(
        publication_id=request.publication_id,
        bibtex=request.bibtex,
        title=parsed.get("title"),
        authors=parsed.get("author"),
        year=int(parsed["year"]) if "year" in parsed else None,
        journal=parsed.get("journal"),
        doi=parsed.get("doi"),
        formatted_ieee=formatted_ieee,
        formatted_elsevier=formatted_elsevier,
        tags=request.tags,
    )
    db.add(citation)
    db.commit()
    db.refresh(citation)
    return citation


@router.get("/citations/", response_model=list[CitationResponse])
def list_citations(
    search: str = None,
    publication_id: int = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List citations."""
    query = db.query(Citation)
    if search:
        query = query.filter(
            (Citation.title.ilike(f"%{search}%")) |
            (Citation.authors.ilike(f"%{search}%"))
        )
    if publication_id:
        query = query.filter(Citation.publication_id == publication_id)

    return query.order_by(Citation.created_at.desc()).offset(skip).limit(limit).all()
