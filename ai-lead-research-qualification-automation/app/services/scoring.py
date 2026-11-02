from dataclasses import dataclass
from .utils import normalize_domain, email_domain

TARGET_INDUSTRIES = {
    "saas", "software", "e-commerce", "ecommerce", "fintech",
    "marketplace", "professional services", "technology"
}
TARGET_COUNTRIES = {
    "united states", "usa", "us", "united kingdom", "uk",
    "canada", "germany", "netherlands", "ireland", "france"
}

@dataclass
class ScoreResult:
    score: float
    qualification: str
    explanation: list[str]

def score_lead(lead, threshold: int = 65) -> ScoreResult:
    if getattr(lead, "suppressed", False):
        return ScoreResult(
            score=0,
            qualification="Suppressed",
            explanation=["Lead is on the suppression list."]
        )

    score = 0
    reasons = []

    industry = (lead.industry or "").strip().lower()
    if industry in TARGET_INDUSTRIES:
        score += 25
        reasons.append("+25 target industry")
    elif industry:
        score += 8
        reasons.append("+8 known non-core industry")

    employees = lead.employee_count or 0
    if 10 <= employees <= 250:
        score += 25
        reasons.append("+25 target employee range (10-250)")
    elif 251 <= employees <= 1000:
        score += 12
        reasons.append("+12 adjacent employee range")

    country = (lead.country or "").strip().lower()
    if country in TARGET_COUNTRIES:
        score += 15
        reasons.append("+15 target geography")

    if lead.pain_point:
        score += 15
        reasons.append("+15 explicit operational need")

    if lead.growth_signal:
        score += 10
        reasons.append("+10 growth signal provided")

    domain = normalize_domain(lead.website)
    mail_domain = email_domain(lead.email)
    if domain:
        score += 5
        reasons.append("+5 website present")
    if domain and mail_domain == domain:
        score += 5
        reasons.append("+5 business email matches website")

    score = min(score, 100)

    if score >= threshold:
        qualification = "Qualified"
    elif score >= 45:
        qualification = "Nurture"
    else:
        qualification = "Low Priority"

    return ScoreResult(score=score, qualification=qualification, explanation=reasons)
