from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class LeadCreate(BaseModel):
    company_name: str
    website: Optional[str] = None
    contact_name: Optional[str] = None
    contact_role: Optional[str] = None
    email: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = Field(default=None, ge=0)
    pain_point: Optional[str] = None
    growth_signal: Optional[str] = None
    suppressed: bool = False

class LeadOut(BaseModel):
    id: int
    company_name: str
    website: Optional[str] = None
    contact_name: Optional[str] = None
    contact_role: Optional[str] = None
    email: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    pain_point: Optional[str] = None
    growth_signal: Optional[str] = None
    research_note: Optional[str] = None
    evidence: Optional[str] = None
    score: float
    score_explanation: Optional[str] = None
    qualification: str
    draft_subject: Optional[str] = None
    draft_body: Optional[str] = None
    approval_status: str
    suppressed: bool

    model_config = {"from_attributes": True}

class ApprovalRequest(BaseModel):
    reviewer_note: Optional[str] = None
