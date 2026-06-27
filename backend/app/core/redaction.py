from __future__ import annotations
import re
from typing import Any

SECRET_RULES = [
    (re.compile(r"sk-[A-Za-z0-9_-]{8,}"), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"AKIA[0-9A-Z]{12,}"), "[REDACTED_AWS_KEY]"),
    (re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[A-Za-z0-9_\-.]{8,}"), "\\1[REDACTED_API_KEY]"),
    (re.compile(r"(?i)(authorization:\s*bearer\s+)[A-Za-z0-9_\-.]{8,}"), "\\1[REDACTED_BEARER_TOKEN]"),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9_\-.]{8,}"), "\\1[REDACTED_BEARER_TOKEN]"),
    (re.compile(r"(?i)(password\s*[:=]\s*)\S+"), "\\1[REDACTED_PASSWORD]"),
]
PII_RULES = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[REDACTED_EMAIL]"),
    (re.compile(r"\+?\d[\d\s-]{9,}\d"), "[REDACTED_PHONE]"),
]

def redact_secrets(value: str | None) -> str:
    text = "" if value is None else str(value)
    for pattern, replacement in SECRET_RULES:
        text = pattern.sub(replacement, text)
    return text

def redact_pii(value: str | None) -> str:
    text = "" if value is None else str(value)
    for pattern, replacement in PII_RULES:
        text = pattern.sub(replacement, text)
    return text

def redact_text(value: str | None, redact_pii: bool = True) -> str:
    text = redact_secrets(value)
    if redact_pii:
        text = globals()["redact_pii"](text)
    return text

def redact_mapping(data: dict[str, Any], redact_pii: bool = True) -> dict[str, Any]:
    out = {}
    for k, v in data.items():
        if isinstance(v, str):
            out[k] = redact_text(v, redact_pii)
        elif isinstance(v, dict):
            out[k] = redact_mapping(v, redact_pii)
        elif isinstance(v, list):
            out[k] = [redact_text(x, redact_pii) if isinstance(x, str) else x for x in v]
        else:
            out[k] = v
    return out
