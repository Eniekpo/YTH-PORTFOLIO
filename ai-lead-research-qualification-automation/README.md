# LeadPilot AI
## AI-Powered Lead Research, Qualification & Outreach Automation System

LeadPilot AI is a portfolio-ready automation project that demonstrates how AI, APIs, workflow orchestration, scoring logic, and human review can work together in a responsible B2B lead-operations process.

The system takes prospect records from CSV or API input, enriches and normalizes the data, scores each company against an Ideal Customer Profile (ICP), drafts evidence-grounded personalized outreach, routes drafts into a human approval queue, and prepares approved leads for CRM/export handoff.

> **Important:** This project does not auto-send outreach by default. Human approval is a required step before a draft can be marked ready for handoff.

## Portfolio Story

**Business problem:** Sales teams spend significant time manually researching prospects, deciding which leads deserve attention, and writing personalized first-touch messages.

**Solution:** A controlled automation pipeline that:
1. standardizes incoming leads;
2. enriches them using deterministic local/demo rules or optional external connectors;
3. calculates an explainable qualification score;
4. creates AI-assisted outreach drafts using only verified lead facts;
5. requires human approval;
6. creates a CRM-ready export and audit log.

## Key Features

- CSV lead import
- Lead normalization and deduplication
- Explainable ICP scoring
- Research/enrichment service abstraction
- Optional LLM integration with safe fallback templates
- Evidence-aware personalization
- Human approval queue
- CRM-ready CSV export
- Webhook-ready API endpoints
- SQLite persistence
- FastAPI REST API
- Streamlit operations dashboard
- n8n workflow example
- Audit trail
- Automated tests
- Docker support
- GitHub Actions CI
- Synthetic demo data

## Architecture

```text
CSV / API Intake
      |
      v
Normalization + Deduplication
      |
      v
Research / Enrichment Layer
      |
      v
ICP Qualification Engine
      |
      +----> Disqualified / Nurture
      |
      v
AI-Assisted Draft Generation
      |
      v
Human Approval Queue
      |
      +----> Rejected / Needs Revision
      |
      v
CRM / Export Handoff
      |
      v
Audit Log + Reporting
```

## Technology Stack

- Python 3.11+
- FastAPI
- Streamlit
- SQLAlchemy
- SQLite
- Pandas
- Pydantic
- Jinja2
- HTTPX
- Pytest
- Docker
- n8n workflow JSON

## Quick Start

See `START_HERE.md` for the fastest local setup.

## Demo Workflow

1. Start the API.
2. Start the Streamlit dashboard.
3. Load the included sample leads.
4. Run enrichment and scoring.
5. Generate outreach drafts.
6. Review drafts in the approval queue.
7. Approve selected leads.
8. Export CRM-ready records.

## Responsible Automation Design

This repository intentionally includes several controls:

- no default bulk email sending;
- a mandatory human approval state;
- no fabricated company facts in draft generation;
- clear evidence fields for personalization;
- deterministic scoring factors;
- opt-out / suppression fields;
- audit logging;
- sample data only.

## Project Structure

```text
.
├── app/
│   ├── api.py
│   ├── dashboard.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   └── services/
│       ├── enrichment.py
│       ├── outreach.py
│       ├── pipeline.py
│       ├── scoring.py
│       └── utils.py
├── automation/
│   └── n8n_lead_workflow.json
├── data/
│   └── sample_leads.csv
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INTERVIEW_TALK_TRACK.md
│   ├── LINKEDIN_PROJECT_COPY.md
│   └── RESPONSIBLE_AUTOMATION.md
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── START_HERE.md
```

## Example Qualification Logic

A lead receives points for signals such as:

- matching target industries;
- target employee range;
- target geography;
- relevant operational need;
- company website present;
- valid business email domain;
- recent growth signal;
- no suppression flag.

The system stores a score explanation rather than returning only a black-box number.

## Example API Endpoints

- `GET /health`
- `POST /leads/import`
- `GET /leads`
- `POST /leads/{lead_id}/enrich`
- `POST /leads/{lead_id}/score`
- `POST /leads/{lead_id}/draft`
- `POST /leads/{lead_id}/approve`
- `POST /leads/{lead_id}/reject`
- `GET /exports/crm`

Interactive API documentation is available at `/docs` when the FastAPI service is running.

## Notes for Employers

This project demonstrates:

- business-process automation;
- API design;
- data validation;
- workflow orchestration;
- explainable scoring;
- LLM integration patterns;
- responsible human-in-the-loop automation;
- operational dashboards;
- database persistence;
- testing and deployment practices.

## License

MIT. Sample data is synthetic.
