from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from .database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    company_name = Column(String(200), nullable=False)
    website = Column(String(300))
    contact_name = Column(String(150))
    contact_role = Column(String(150))
    email = Column(String(250))
    industry = Column(String(120))
    country = Column(String(100))
    employee_count = Column(Integer)
    source = Column(String(100), default="csv")
    pain_point = Column(String(300))
    growth_signal = Column(String(300))
    research_note = Column(Text)
    evidence = Column(Text)
    score = Column(Float, default=0)
    score_explanation = Column(Text)
    qualification = Column(String(50), default="Unscored")
    draft_subject = Column(String(250))
    draft_body = Column(Text)
    approval_status = Column(String(50), default="Not Drafted")
    suppressed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer)
    action = Column(String(100), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
