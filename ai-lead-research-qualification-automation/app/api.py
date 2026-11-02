from io import StringIO
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd

from .database import Base, engine, get_db
from .models import Lead, AuditLog
from .schemas import LeadOut, ApprovalRequest
from .services.pipeline import enrich_and_score, draft_for_lead, log_action, run_pipeline

Base.metadata.create_all(bind=engine)
app = FastAPI(title="LeadPilot AI API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok", "service": "LeadPilot AI"}

@app.get("/leads", response_model=list[LeadOut])
def list_leads(db: Session = Depends(get_db)):
    return db.query(Lead).order_by(Lead.score.desc(), Lead.id.asc()).all()

@app.post("/leads/import")
async def import_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = await file.read()
    try:
        df = pd.read_csv(StringIO(raw.decode("utf-8")))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {exc}")

    required = {"company_name"}
    if not required.issubset(df.columns):
        raise HTTPException(status_code=400, detail="CSV must include company_name")

    inserted = 0
    for row in df.to_dict(orient="records"):
        data = {k: (None if pd.isna(v) else v) for k, v in row.items()}
        if "employee_count" in data and data["employee_count"] is not None:
            data["employee_count"] = int(data["employee_count"])
        if "suppressed" in data:
            data["suppressed"] = str(data["suppressed"]).lower() in {"true", "1", "yes"}
        valid_cols = {c.name for c in Lead.__table__.columns if c.name not in {"id", "created_at", "updated_at"}}
        data = {k: v for k, v in data.items() if k in valid_cols}
        db.add(Lead(**data))
        inserted += 1
    db.commit()
    return {"inserted": inserted}

def get_lead_or_404(db, lead_id):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@app.post("/leads/{lead_id}/enrich", response_model=LeadOut)
def enrich(lead_id: int, db: Session = Depends(get_db)):
    lead = get_lead_or_404(db, lead_id)
    return enrich_and_score(db, lead)

@app.post("/leads/{lead_id}/score", response_model=LeadOut)
def score(lead_id: int, db: Session = Depends(get_db)):
    lead = get_lead_or_404(db, lead_id)
    return enrich_and_score(db, lead)

@app.post("/leads/{lead_id}/draft", response_model=LeadOut)
def draft(lead_id: int, db: Session = Depends(get_db)):
    lead = get_lead_or_404(db, lead_id)
    try:
        return draft_for_lead(db, lead)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/leads/{lead_id}/approve", response_model=LeadOut)
def approve(lead_id: int, payload: ApprovalRequest, db: Session = Depends(get_db)):
    lead = get_lead_or_404(db, lead_id)
    if lead.approval_status != "Pending Review":
        raise HTTPException(status_code=400, detail="Lead must be pending review.")
    lead.approval_status = "Approved for Handoff"
    db.commit()
    db.refresh(lead)
    log_action(db, lead.id, "APPROVED", payload.reviewer_note or "")
    return lead

@app.post("/leads/{lead_id}/reject", response_model=LeadOut)
def reject(lead_id: int, payload: ApprovalRequest, db: Session = Depends(get_db)):
    lead = get_lead_or_404(db, lead_id)
    lead.approval_status = "Rejected"
    db.commit()
    db.refresh(lead)
    log_action(db, lead.id, "REJECTED", payload.reviewer_note or "")
    return lead

@app.post("/pipeline/run")
def pipeline_run(db: Session = Depends(get_db)):
    results = run_pipeline(db)
    return {
        "processed": len(results),
        "qualified": sum(1 for x in results if x.qualification == "Qualified"),
        "pending_review": sum(1 for x in results if x.approval_status == "Pending Review"),
    }

@app.get("/audit")
def audit(db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(500).all()
    return [
        {
            "id": r.id,
            "lead_id": r.lead_id,
            "action": r.action,
            "details": r.details,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]

@app.get("/exports/crm")
def export_crm(db: Session = Depends(get_db)):
    rows = db.query(Lead).filter(Lead.approval_status == "Approved for Handoff").all()
    data = [{
        "company_name": r.company_name,
        "website": r.website,
        "contact_name": r.contact_name,
        "contact_role": r.contact_role,
        "email": r.email,
        "industry": r.industry,
        "country": r.country,
        "employee_count": r.employee_count,
        "qualification_score": r.score,
        "draft_subject": r.draft_subject,
        "draft_body": r.draft_body,
        "handoff_status": r.approval_status,
    } for r in rows]
    df = pd.DataFrame(data)
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=crm_ready_leads.csv"},
    )
