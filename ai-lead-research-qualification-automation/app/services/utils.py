import re
from urllib.parse import urlparse

def normalize_domain(website: str | None) -> str:
    if not website:
        return ""
    value = website.strip().lower()
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = urlparse(value)
    return parsed.netloc.replace("www.", "")

def email_domain(email: str | None) -> str:
    if not email or "@" not in email:
        return ""
    return email.split("@", 1)[1].lower().strip()

def clean_text(value):
    if value is None:
        return None
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value or None
