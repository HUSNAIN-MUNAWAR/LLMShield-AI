from __future__ import annotations
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.audit_log import AuditLog
router=APIRouter(prefix="/audit-logs", tags=["audit"])
@router.get("")
def list_audit_logs(db: Session = Depends(get_db)):
    rows=db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [{"id":r.id,"actor_email":r.actor_email,"action":r.action,"resource_type":r.resource_type,"resource_id":r.resource_id,"status":r.status,"detail":json.loads(r.detail_json or "{}"),"created_at":r.created_at.isoformat()} for r in rows]
