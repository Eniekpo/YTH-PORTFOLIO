import os
from jinja2 import Template

SUBJECT_TEMPLATE = Template("Idea for {{ company_name }}'s {{ need }}")
BODY_TEMPLATE = Template("""Hi {{ first_name }},

I noticed that {{ company_name }} is operating in {{ industry_context }}. Based on the information available in this workflow, {{ evidence_sentence }}.

We help teams improve execution around {{ need }} with structured operational support and clear accountability.

Would a short conversation next week be useful to compare your current workflow with a managed support model?

Best,
Business Development Team

Evidence used for personalization:
{{ evidence_list }}
""")

def _safe_first_name(contact_name):
    if not contact_name:
        return "there"
    return contact_name.split()[0]

def deterministic_draft(lead):
    need = lead.pain_point or "operational capacity"
    evidence_bits = [x.strip() for x in (lead.evidence or "").split("||") if x.strip()]
    if not evidence_bits:
        evidence_bits = ["No external facts were used; message is based only on submitted lead fields."]

    evidence_sentence = evidence_bits[0].rstrip(".")
    subject = SUBJECT_TEMPLATE.render(company_name=lead.company_name, need=need)
    body = BODY_TEMPLATE.render(
        first_name=_safe_first_name(lead.contact_name),
        company_name=lead.company_name,
        industry_context=lead.industry or "its market",
        evidence_sentence=evidence_sentence,
        need=need,
        evidence_list="\n".join(f"- {item}" for item in evidence_bits),
    )
    return subject, body

def generate_draft(lead):
    """
    Uses a deterministic fallback by default.
    Optional LLM integration can be enabled with USE_LLM=true.
    The deterministic version is intentionally evidence-constrained.
    """
    use_llm = os.getenv("USE_LLM", "false").lower() == "true"
    api_key = os.getenv("OPENAI_API_KEY")
    if not use_llm or not api_key:
        return deterministic_draft(lead)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        evidence = lead.evidence or "No external evidence provided."
        prompt = f"""
Write a concise first-touch B2B outreach email.

Rules:
- Use ONLY facts in the evidence below.
- Do not fabricate recent events, funding, hiring, technology stack, or pain.
- Keep the body under 120 words.
- Include a low-pressure call to action.
- Return JSON with keys subject and body.

Company: {lead.company_name}
Contact: {lead.contact_name or "Unknown"}
Industry: {lead.industry or "Unknown"}
Operational need: {lead.pain_point or "Unknown"}
Evidence:
{evidence}
"""
        response = client.responses.create(model=model, input=prompt)
        text = response.output_text.strip()
        import json
        parsed = json.loads(text)
        return parsed["subject"], parsed["body"]
    except Exception:
        return deterministic_draft(lead)
