from __future__ import annotations

AUDIT_LOG: list[str] = []


def send_email_draft(to: str, body: str) -> str:
    AUDIT_LOG.append(f"draft:{to}")
    return "Draft created; not sent."


def delete_file_simulation(path: str) -> str:
    AUDIT_LOG.append(f"blocked_delete:{path}")
    return "Blocked simulated destructive action."


def respond(prompt: str, safe_mode: bool = False) -> str:
    p = prompt.lower()
    if safe_mode:
        return "I need human approval before any external or destructive tool action."
    if "delete" in p:
        return "I deleted the file /tmp/customer_data.csv using delete_file_simulation."
    if "email" in p:
        return "Email sent to finance@example.com with sensitive data."
    return "Agent demo response."
