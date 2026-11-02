from types import SimpleNamespace
from app.services.scoring import score_lead

def make_lead(**kwargs):
    base = dict(
        industry="SaaS",
        employee_count=50,
        country="United States",
        pain_point="customer support scaling",
        growth_signal="expanding operations",
        website="https://example.com",
        email="alex@example.com",
        suppressed=False,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)

def test_strong_fit_is_qualified():
    result = score_lead(make_lead())
    assert result.score >= 65
    assert result.qualification == "Qualified"

def test_suppressed_lead_is_blocked():
    result = score_lead(make_lead(suppressed=True))
    assert result.score == 0
    assert result.qualification == "Suppressed"

def test_low_fit_is_not_qualified():
    result = score_lead(make_lead(
        industry="Construction",
        employee_count=3,
        country="Brazil",
        pain_point=None,
        growth_signal=None,
        website=None,
        email=None,
    ))
    assert result.qualification != "Qualified"
