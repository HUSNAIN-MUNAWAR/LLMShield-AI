from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.url_safety import validate_target_url
from app.models.target import Target
from app.schemas.target import TargetCreate, TargetRead
from app.services.target_clients import TargetClient, TargetConfig
router=APIRouter(prefix="/targets", tags=["targets"])
@router.post("", response_model=TargetRead)
def create_target(payload: TargetCreate, db: Session = Depends(get_db)):
    if payload.type=="custom_http" and payload.endpoint_url:
        safety=validate_target_url(payload.endpoint_url, allow_private=settings.allow_private_targets)
        if not safety.allowed: raise HTTPException(status_code=400, detail=safety.reason)
    target=Target(name=payload.name,type=payload.type,endpoint_url=payload.endpoint_url,safe_mode=payload.safe_mode,config_json=json.dumps(payload.config or {}))
    db.add(target); db.commit(); db.refresh(target); return target
@router.get("", response_model=list[TargetRead])
def list_targets(db: Session = Depends(get_db)): return list(db.query(Target).order_by(Target.created_at.desc()).all())
@router.get("/{target_id}", response_model=TargetRead)
def get_target(target_id: str, db: Session = Depends(get_db)):
    target=db.get(Target,target_id)
    if not target: raise HTTPException(status_code=404, detail="Target not found")
    return target
@router.delete("/{target_id}")
def delete_target(target_id: str, db: Session = Depends(get_db)):
    target=db.get(Target,target_id)
    if not target: raise HTTPException(status_code=404, detail="Target not found")
    db.delete(target); db.commit(); return {"status":"deleted","id":target_id}
@router.post("/{target_id}/test")
def test_target(target_id: str, db: Session = Depends(get_db)):
    target=db.get(Target,target_id)
    if not target: raise HTTPException(status_code=404, detail="Target not found")
    cfg=TargetConfig(target.id,target.name,target.type,target.endpoint_url,target.safe_mode,json.loads(target.config_json or "{}"))
    response=TargetClient().send_prompt(cfg,"Authorized local connection test. Respond safely.")
    return {"status":"ok" if not response.error else "error","provider":response.provider,"latency_ms":response.latency_ms,"error":response.error}
