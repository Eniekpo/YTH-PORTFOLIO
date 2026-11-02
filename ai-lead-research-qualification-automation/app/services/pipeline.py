import os
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Lead, AuditLog
from .enrichment import enrich_lead
from .scoring import score_lead
from .outreach import generate_draft

def log_action(db: Session, lead_id: int, action: str, details: str = ""):
    db.add(AuditLog(lead_id=lead_id, action=action, details=details))
    db.commit()

def enrich_and_score(db: Session, lead: Lead):
    enrichment = enrich_lead(lead)
    lead.research_note = enrichment.research_note
    lead.evidence = "||".join(enrichment.evidence)

    threshold = int(os.getenv("MIN_QUALIFIED_SCORE", "65"))
    result = score_lead(lead, threshold=threshold)
    lead.score = result.score
    lead.qualification = result.qualification
    lead.score_explanation = " | ".join(result.explanation)
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    log_action(db, lead.id, "ENRICH_AND_SCORE", lead.score_explanation or "")
    return lead

def draft_for_lead(db: Session, lead: Lead):
    if lead.suppressed:
        raise ValueError("Suppressed leads cannot receive outreach drafts.")
    if lead.qualification != "Qualified":
        raise ValueError("Only qualified leads can enter the outreach draft stage.")

    subject, body = generate_draft(lead)
    lead.draft_subject = subject
    lead.draft_body = body
    lead.approval_status = "Pending Review"
    db.commit()
    db.refresh(lead)
    log_action(db, lead.id, "DRAFT_CREATED", subject)
    return lead

def run_pipeline(db: Session):
    leads = db.query(Lead).all()
    results = []
    for lead in leads:
        enrich_and_score(db, lead)
        if lead.qualification == "Qualified" and not lead.suppressed:
            try:
                draft_for_lead(db, lead)
            except ValueError:
                pass
        results.append(lead)
    return results
