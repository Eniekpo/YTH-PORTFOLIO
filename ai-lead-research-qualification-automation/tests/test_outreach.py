from types import SimpleNamespace
from app.services.outreach import deterministic_draft

def test_draft_uses_evidence():
    lead = SimpleNamespace(
        company_name="Northstar SaaS",
        contact_name="Alex Morgan",
        industry="SaaS",
        pain_point="customer support scaling",
        evidence="Declared industry: SaaS||Provided operational need: customer support scaling",
    )
    subject, body = deterministic_draft(lead)
    assert "Northstar SaaS" in subject
    assert "Declared industry: SaaS" in body
    assert "Evidence used for personalization" in body
