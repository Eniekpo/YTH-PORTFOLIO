# InsightForge — Market Research & Survey Analytics SaaS

A portfolio-ready full-stack web application for turning raw survey files into structured market-research analysis. The project demonstrates **full-stack engineering + applied statistics + research workflow design** in one deployable application.

> **Portfolio note:** The included demo dataset is synthetic and created specifically for this project. It does not represent a real client or real respondents.

## What the application does

- Secure local account registration and login
- Create and manage research projects
- Upload CSV or Excel survey-response datasets
- Persist project/dataset metadata in SQLite
- Profile response counts, variables, completeness and missingness
- Explore categorical frequency distributions with interactive charts
- Run cross-tabulations with row percentages
- Calculate chi-square tests of association
- Generate numeric descriptive statistics and correlation data through the API
- Produce an automated, evidence-grounded research snapshot
- Export analysis to **Excel** and **PDF**
- Run with local development commands or Docker Compose
- Validate analytics logic with automated tests

## Architecture

```text
React + Vite + Recharts
        |
        | REST / Bearer token
        v
FastAPI application
 ├── Authentication
 ├── Research Projects
 ├── Dataset Uploads
 ├── Survey Analytics
 ├── Automated Insights
 └── PDF / Excel Reports
        |
        ├── SQLite / SQLAlchemy metadata
        └── CSV / Excel response files
```

## Project structure

```text
market-research-survey-analytics-saas/
├── backend/
│   ├── app/
│   │   ├── routers/          # REST endpoints
│   │   ├── analytics.py      # Survey/statistical functions
│   │   ├── auth.py           # PBKDF2 passwords + signed tokens
│   │   ├── insights.py       # Evidence-grounded narratives
│   │   ├── models.py         # SQLAlchemy entities
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/pages/
│   ├── src/App.jsx
│   ├── src/api.js
│   └── src/styles.css
├── data/
│   └── demo_customer_experience_survey.csv
├── docs/
├── docker-compose.yml
└── README.md
```

## Local setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm

### 1. Backend

**Windows**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**macOS/Linux**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

API documentation: `http://localhost:8000/docs`

### 2. Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

### 3. Demo account

Run this once from the repository root after installing backend dependencies:

```bash
python scripts/setup_demo.py
```

Then log in with:

- Email: `demo@insightforge.dev`
- Password: `portfolio123`

A synthetic demo survey is included at `data/demo_customer_experience_survey.csv`. After logging in, open the seeded project and upload this CSV.

## Docker setup

```bash
docker compose up --build
```

Then open `http://localhost:5173`.

## Run tests

```bash
PYTHONPATH=backend pytest backend/tests -q
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="backend"
pytest backend/tests -q
```

## API highlights

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Authenticate |
| GET/POST | `/api/projects` | List/create research projects |
| POST | `/api/projects/{id}/datasets` | Upload responses |
| GET | `/api/analysis/{id}/overview` | Survey quality/profile |
| GET | `/api/analysis/{id}/frequency` | Frequency table |
| GET | `/api/analysis/{id}/crosstab` | Cross-tab + chi-square |
| GET | `/api/analysis/{id}/numeric` | Numeric summary |
| GET | `/api/analysis/{id}/correlation` | Correlation matrix |
| GET | `/api/analysis/{id}/insights` | Automated research snapshot |
| GET | `/api/reports/{id}/xlsx` | Excel export |
| GET | `/api/reports/{id}/pdf` | PDF export |

## Statistical design choices

The application intentionally separates **descriptive evidence** from interpretation. Its automated narrative reports counts, shares, means, medians, ranges and missingness. It does not claim causality from cross-sectional survey data.

The cross-tab analysis reports a chi-square test when the contingency table has enough structure for the calculation. A statistically significant association should still be interpreted with sampling design, representativeness, weighting, multiplicity and practical importance in mind.

## Security note

Authentication is deliberately self-contained for a local portfolio application. Passwords are salted and hashed with PBKDF2-HMAC-SHA256, and signed bearer tokens expire after 12 hours.

For production, use a managed identity provider or a hardened session/JWT implementation, HTTPS, rate limiting, secrets management, PostgreSQL, object storage, virus scanning for uploads, and tighter CORS settings.

## Suggested next-stage enhancements

- Survey weighting and weighted estimates
- Multiple-response question handling
- Significance testing between proportions
- Saved filters and analysis views
- Organization/team workspaces
- Role-based access control
- Object storage for uploads
- PostgreSQL production database
- Background jobs for large datasets
- Optional LLM provider with prompt/version logging and human review

See `docs/PORTFOLIO_NOTES.md` for interview positioning and `docs/LINKEDIN_POST.md` for a ready-to-edit project post.
