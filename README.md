# Antenna ML Research Hub

Integrated research assistant for antenna engineering workflows: simulation data import, ML model training, publication-quality visualization, and paper formatting.

Built for mmWave MIMO antenna research (28/38 GHz) with support for CST, HFSS, and VNA data formats.

## Features

- **Dataset Manager** - Import CST .txt, HFSS .csv, VNA .s2p files with auto-format detection
- **Data Alignment** - Align measured vs simulated data onto common frequency grids
- **Synthetic Data** - Physics-informed scaling (f1/f2 = L2/L1) for frequency translation
- **ML Pipeline** - One-click training of 5 models (Linear Regression, Random Forest, Gradient Boosting, SVR, Neural Network)
- **Publication Assistant** - IEEE/Elsevier-compliant figures, LaTeX tables, research highlights, citation formatting
- **Knowledge Base** - Antenna design library with cross-referencing and insights
- **Quick Actions** - Unit converter, wavelength calculator, geometry scaler

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL |
| ML | PyTorch, scikit-learn, pandas, numpy, scipy |
| Frontend | React 18, TypeScript, TailwindCSS, Plotly.js |
| Visualization | matplotlib (publication), Plotly (interactive) |
| Infrastructure | Docker, Alembic |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### Using Docker (Recommended)

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- FastAPI backend on port 8000
- React frontend on port 3000

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
```bash
docker-compose up -d db
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/datasets/upload` | Upload and parse a dataset |
| POST | `/api/datasets/align` | Align two datasets |
| POST | `/api/datasets/synthetic` | Generate synthetic data |
| POST | `/api/models/train` | Train ML models |
| POST | `/api/models/predict` | Make predictions |
| POST | `/api/visualizations/generate` | Generate publication figures |
| POST | `/api/publications/latex-table` | Generate LaTeX tables |
| POST | `/api/publications/highlights` | Generate research highlights |
| POST | `/api/publications/citations` | Format BibTeX citations |
| GET | `/api/knowledge-base/insights` | Research insights |
| POST | `/api/quick-actions/convert-unit` | Unit conversion |

## Project Structure

```
antenna-ml-research-hub/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # API endpoints
│   │   ├── core/                # Config, database
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── data_parser.py       # CST/HFSS/VNA parsing
│   │   │   ├── data_alignment.py    # Frequency grid alignment
│   │   │   ├── ml_pipeline.py       # 5-model training pipeline
│   │   │   ├── figure_generator.py  # Publication figures
│   │   │   ├── publication_tools.py # LaTeX, highlights, citations
│   │   │   └── synthetic_data.py    # EM scaling
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page views
│   │   ├── services/api.ts      # API client
│   │   └── types/index.ts       # TypeScript types
│   └── package.json
├── storage/                     # File storage
├── docker-compose.yml
└── README.md
```

## Supported File Formats

| Format | Extension | Source |
|--------|-----------|--------|
| CST Export | .txt | CST Microwave Studio |
| HFSS Export | .csv | Ansys HFSS |
| Touchstone | .s1p, .s2p | VNA measurements |
| Generic CSV | .csv | Any tool |

---

Built for antenna researchers. Reduces 3-hour tasks to 5-minute operations.
