# Start Here

## 1. Create a virtual environment

### Windows
```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Create the demo database

```bash
python -m app.seed
```

Or initialize the database **and** run the complete demo automation in one command:

```bash
python run_demo.py
```

## 4. Start the API

```bash
uvicorn app.api:app --reload --port 8000
```

Open:
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 5. Start the dashboard

In another terminal:

```bash
streamlit run app/dashboard.py
```

Open:
- Dashboard: http://localhost:8501

## 6. Demo the workflow

Inside the dashboard:

1. Review the imported demo leads.
2. Run the automation pipeline.
3. Inspect explainable qualification scores.
4. Review generated outreach drafts.
5. Approve or reject drafts manually.
6. Export approved CRM-ready records.

## Optional OpenAI integration

The project works without any API key using a deterministic template engine.

To enable optional LLM-assisted drafting:

1. Copy `.env.example` to `.env`.
2. Add your API key.
3. Set:

```env
USE_LLM=true
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

The application will still require human approval before any handoff.

## Run tests

```bash
pytest -q
```

## Docker

```bash
docker compose up --build
```
