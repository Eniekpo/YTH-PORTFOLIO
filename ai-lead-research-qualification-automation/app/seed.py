from pathlib import Path
import pandas as pd
from .database import Base, engine, SessionLocal
from .models import Lead

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "sample_leads.csv"

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Lead).count() > 0:
            print("Database already contains leads. Skipping seed.")
            return
        df = pd.read_csv(CSV_PATH)
        for row in df.to_dict(orient="records"):
            clean = {}
            for k, v in row.items():
                if pd.isna(v):
                    clean[k] = None
                else:
                    clean[k] = v
            clean["employee_count"] = int(clean["employee_count"]) if clean.get("employee_count") is not None else None
            clean["suppressed"] = str(clean.get("suppressed", "false")).lower() in {"true", "1", "yes"}
            db.add(Lead(**clean))
        db.commit()
        print(f"Seeded {len(df)} synthetic leads.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
