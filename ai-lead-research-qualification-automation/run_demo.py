from app.seed import seed
from app.database import SessionLocal
from app.services.pipeline import run_pipeline

if __name__ == '__main__':
    seed()
    db = SessionLocal()
    try:
        results = run_pipeline(db)
        print(f'Processed {len(results)} leads.')
        print(f"Qualified: {sum(x.qualification == 'Qualified' for x in results)}")
        print(f"Pending review: {sum(x.approval_status == 'Pending Review' for x in results)}")
        print('Launch the dashboard with: streamlit run app/dashboard.py')
    finally:
        db.close()
