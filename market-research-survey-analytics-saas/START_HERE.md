# Start Here

## Fastest local setup

1. Open a terminal in the project folder.
2. Create and activate a Python virtual environment.
3. Install backend dependencies: `pip install -r backend/requirements.txt`.
4. Create the demo account/project: `python scripts/setup_demo.py`.
5. Start the API: `cd backend && python -m uvicorn app.main:app --reload --port 8000`.
6. Open a second terminal, run `cd frontend && npm install && npm run dev`.
7. Visit `http://localhost:5173`.
8. Sign in with `demo@insightforge.dev` / `portfolio123`.
9. Upload `data/demo_customer_experience_survey.csv` into the seeded Customer Experience Study project.

API documentation is available at `http://localhost:8000/docs`.

For Docker users, run `docker compose up --build` from the project root.
