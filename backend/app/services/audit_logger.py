from __future__ import annotations
import json
from typing import Any
from sqlalchemy.orm import Session
from app.core.redaction import redact_mapping
from app.models.audit_log import AuditLog
from app.models.user import User
def audit(db: Session, action: str, *, actor: User | None = None, resource_type: str = "system", resource_id: str | None = None, status: str = "success", detail: dict[str, Any] | None = None) -> AuditLog:
    row=AuditLog(actor_id=actor.id if actor else None, actor_email=actor.email if actor else None, action=action, resource_type=resource_type, resource_id=resource_id, status=status, detail_json=json.dumps(redact_mapping(detail or {})))
    db.add(row); db.commit(); db.refresh(row); return row
