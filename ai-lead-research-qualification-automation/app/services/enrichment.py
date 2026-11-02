from dataclasses import dataclass
from .utils import normalize_domain, email_domain

@dataclass
class EnrichmentResult:
    research_note: str
    evidence: list[str]

TARGET_INDUSTRIES = {
    "saas", "software", "e-commerce", "ecommerce", "fintech",
    "marketplace", "professional services", "technology"
}

def enrich_lead(lead) -> EnrichmentResult:
    """
    Deterministic local enrichment used for the portfolio demo.
    In production this service can be swapped for approved data providers/APIs.
    It deliberately does not invent unverifiable external facts.
    """
    evidence = []
    domain = normalize_domain(lead.website)
    mail_domain = email_domain(lead.email)

    if domain:
        evidence.append(f"Website domain available: {domain}")
    if mail_domain and domain and mail_domain == domain:
        evidence.append("Contact email domain matches company website")
    if lead.industry:
        evidence.append(f"Declared industry: {lead.industry}")
    if lead.employee_count is not None:
        evidence.append(f"Declared employee count: {lead.employee_count}")
    if lead.growth_signal:
        evidence.append(f"Provided growth signal: {lead.growth_signal}")
    if lead.pain_point:
        evidence.append(f"Provided operational need: {lead.pain_point}")

    note = " | ".join(evidence) if evidence else "No enrichment evidence available."
    return EnrichmentResult(research_note=note, evidence=evidence)
