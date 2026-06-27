from __future__ import annotations
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import require_role
from app.core.database import get_db
from app.core.security import generate_api_key, hash_api_key
from app.models.api_key import ApiKey
from app.models.user import User
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated
from app.services.audit_logger import audit

router=APIRouter(prefix="/api-keys", tags=["api-keys"])
ALLOWED_SCOPES={"ci_runner","viewer","analyst"}

@router.post("", response_model=ApiKeyCreated)
def create_api_key(payload: ApiKeyCreate, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))):
    scope=payload.scoped_role if payload.scoped_role in ALLOWED_SCOPES else "ci_runner"
    key=generate_api_key(); prefix="_".join(key.split("_")[:2])[:24]
    row=ApiKey(name=payload.name, key_prefix=prefix, key_hash=hash_api_key(key), scoped_role=scope, owner_user_id=user.id, notes=payload.notes)
    db.add(row); db.commit(); db.refresh(row); audit(db,"api_key_create",actor=user,detail={"scope":scope,"name":payload.name})
    return ApiKeyCreated(id=row.id,name=row.name,key_prefix=row.key_prefix,scoped_role=row.scoped_role,api_key=key)

@router.get("")
def list_api_keys(db: Session = Depends(get_db), user: User = Depends(require_role("admin"))):
    rows=db.query(ApiKey).order_by(ApiKey.created_at.desc()).all()
    return [{"id":r.id,"name":r.name,"key_prefix":r.key_prefix,"scoped_role":r.scoped_role,"is_active":r.is_active,"created_at":r.created_at.isoformat() if r.created_at else None,"last_used_at":r.last_used_at.isoformat() if r.last_used_at else None,"revoked_at":r.revoked_at.isoformat() if r.revoked_at else None} for r in rows]

@router.delete("/{api_key_id}")
def revoke_api_key(api_key_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))):
    row=db.get(ApiKey, api_key_id)
    if not row: raise HTTPException(status_code=404, detail="API key not found")
    row.is_active=False; row.revoked_at=datetime.now(timezone.utc); db.commit(); audit(db,"api_key_revoke",actor=user,detail={"api_key_id":api_key_id})
    return {"status":"revoked","id":api_key_id}
