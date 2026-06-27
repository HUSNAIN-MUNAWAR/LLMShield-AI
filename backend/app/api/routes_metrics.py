from __future__ import annotations
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.finding import Finding
from app.models.scan import Scan
router=APIRouter(tags=["metrics"])
@router.get("/metrics")
def metrics(db: Session = Depends(get_db)) -> Response:
    scans=db.query(Scan).count(); findings=db.query(Finding).count(); critical=db.query(Finding).filter(Finding.severity=="critical").count(); completed=db.query(Scan).filter(Scan.status=="completed").count()
    body=f"""# HELP llmshield_scans_total Total scans recorded
# TYPE llmshield_scans_total counter
llmshield_scans_total {scans}
# HELP llmshield_findings_total Total findings recorded
# TYPE llmshield_findings_total counter
llmshield_findings_total {findings}
llmshield_critical_findings_total {critical}
llmshield_completed_scans_total {completed}
llmshield_provider_latency_ms 0
llmshield_scan_duration_seconds 0
llmshield_tests_executed_total {findings}
"""
    return Response(body, media_type="text/plain; version=0.0.4")
