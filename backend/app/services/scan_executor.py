from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.finding import Finding
from app.models.scan import Scan
from app.models.target import Target
from app.services.audit_logger import audit
from app.services.scanner import ScannerService
from app.services.target_clients import TargetConfig

def execute_scan(scan_id: str) -> dict:
    db: Session = SessionLocal()
    try:
        scan=db.get(Scan, scan_id)
        if not scan: return {"status":"failed","error":"scan not found"}
        target=db.get(Target, scan.target_id)
        if not target:
            scan.status="failed"; scan.failed_at=datetime.now(timezone.utc); scan.error_message="Target not found"; db.commit(); return {"status":"failed","error":"target not found"}
        scan.status="running"; scan.started_at=scan.started_at or datetime.now(timezone.utc); scan.error_message=None; db.query(Finding).filter(Finding.scan_id==scan_id).delete(); db.commit()
        cfg=TargetConfig(id=target.id,name=target.name,type=target.type,endpoint_url=target.endpoint_url,safe_mode=target.safe_mode,config=json.loads(target.config_json or "{}"))
        result=ScannerService().run_scan(cfg,json.loads(scan.selected_packs_json or "[]"),scan_id=scan.id)
        cols=set(Finding.__table__.columns.keys())
        for item in result.findings:
            db.add(Finding(**{k:v for k,v in item.items() if k in cols}))
        scan.status=result.status; scan.total_tests=result.total_tests; scan.failed_tests=result.failed_tests; scan.passed_tests=result.passed_tests; scan.risk_score=result.risk_score; scan.progress=100 if result.status=="completed" else scan.progress
        if result.status=="completed": scan.completed_at=datetime.now(timezone.utc)
        if result.status=="cancelled": scan.cancelled_at=datetime.now(timezone.utc)
        db.commit(); audit(db,"scan_execute",detail={"scan_id":scan_id,"status":result.status,"total_tests":result.total_tests})
        return {"status":result.status,"scan_id":scan_id,"total_tests":result.total_tests,"risk_score":result.risk_score}
    except Exception as exc:
        scan=db.get(Scan, scan_id) if 'scan' not in locals() else scan
        if scan:
            scan.status="failed"; scan.failed_at=datetime.now(timezone.utc); scan.error_message=str(exc)[:500]; db.commit()
        return {"status":"failed","scan_id":scan_id,"error":str(exc)[:500]}
    finally:
        db.close()
