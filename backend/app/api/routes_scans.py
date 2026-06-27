from __future__ import annotations
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.finding import Finding
from app.models.scan import Scan
from app.models.target import Target
from app.schemas.scan import ScanCreate, ScanRead, ScanSummary
from app.core.config import settings
from app.services.scan_executor import execute_scan
from app.services.scan_queue import cancel_scan, create_status, get_status
from app.workers.queue import enqueue_scan
from app.services.scanner import ScannerService, category_distribution, severity_distribution
from app.services.target_clients import TargetConfig
router=APIRouter(prefix="/scans", tags=["scans"])
@router.post("", response_model=ScanRead)
def create_scan(payload: ScanCreate, db: Session = Depends(get_db)):
    target=db.get(Target,payload.target_id)
    if not target: raise HTTPException(status_code=404, detail="Target not found")
    scan=Scan(target_id=payload.target_id, selected_packs_json=json.dumps(payload.attack_pack_ids), options_json=json.dumps(payload.options))
    db.add(scan); db.commit(); db.refresh(scan); return scan
@router.get("", response_model=list[ScanRead])
def list_scans(db: Session = Depends(get_db)): return list(db.query(Scan).order_by(Scan.created_at.desc()).all())
@router.get("/{scan_id}", response_model=ScanRead)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    scan=db.get(Scan,scan_id)
    if not scan: raise HTTPException(status_code=404, detail="Scan not found")
    return scan
@router.post("/{scan_id}/run", response_model=ScanRead)
def run_scan(scan_id: str, db: Session = Depends(get_db)):
    scan=db.get(Scan,scan_id)
    if not scan: raise HTTPException(status_code=404, detail="Scan not found")
    target=db.get(Target,scan.target_id)
    if not target: raise HTTPException(status_code=404, detail="Target not found")
    db.query(Finding).filter(Finding.scan_id==scan_id).delete(); db.commit()
    if settings.scan_execution_mode == "async":
        result=enqueue_scan(scan.id)
        scan.status="queued"; scan.job_id=result.job_id; scan.progress=0; scan.started_at=None; scan.error_message=None if result.queued else result.message
        db.commit(); db.refresh(scan); return scan
    # Local/simple mode uses the same executor path synchronously for deterministic demo reliability.
    create_status(scan.id,f"sync-{scan.id[:8]}")
    execute_scan(scan.id)
    db.refresh(scan); return scan
@router.get("/{scan_id}/status")
def scan_status(scan_id: str, db: Session = Depends(get_db)):
    scan=db.get(Scan,scan_id)
    if not scan: raise HTTPException(status_code=404, detail="Scan not found")
    mem=get_status(scan_id)
    return {"scan_id":scan.id,"job_id":scan.job_id or mem.job_id,"status":scan.status or mem.status,"progress":max(scan.progress or 0, mem.progress),"current_test":mem.current_test or scan.current_test,"started_at":scan.started_at.isoformat() if scan.started_at else mem.started_at,"completed_at":scan.completed_at.isoformat() if scan.completed_at else mem.completed_at,"error_message":scan.error_message or mem.error_message}
@router.post("/{scan_id}/cancel")
def cancel(scan_id: str, db: Session = Depends(get_db)):
    scan=db.get(Scan,scan_id)
    if not scan: raise HTTPException(status_code=404, detail="Scan not found")
    cancel_scan(scan_id); scan.status="cancelled"; scan.cancelled_at=datetime.now(timezone.utc); db.commit(); return {"status":"cancelled","scan_id":scan_id}
@router.get("/{scan_id}/events")
def scan_events(scan_id: str): return {"event":"status","data":get_status(scan_id).__dict__}
@router.get("/{scan_id}/findings")
def get_scan_findings(scan_id: str, db: Session = Depends(get_db)):
    return [{k:v for k,v in f.__dict__.items() if not k.startswith("_")} for f in db.query(Finding).filter(Finding.scan_id==scan_id).all()]
@router.get("/{scan_id}/summary", response_model=ScanSummary)
def get_scan_summary(scan_id: str, db: Session = Depends(get_db)):
    scan=db.get(Scan,scan_id)
    if not scan: raise HTTPException(status_code=404, detail="Scan not found")
    findings=[{"severity":f.severity,"category":f.category,"passed":f.passed,"risk_score":f.risk_score} for f in db.query(Finding).filter(Finding.scan_id==scan_id).all()]
    return ScanSummary(scan_id=scan.id,status=scan.status,total_tests=scan.total_tests,passed_tests=scan.passed_tests,failed_tests=scan.failed_tests,risk_score=scan.risk_score,severity_distribution=severity_distribution(findings),category_distribution=category_distribution(findings))
