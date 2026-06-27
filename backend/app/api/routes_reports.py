from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.finding import Finding
from app.models.report import Report
from app.models.scan import Scan
from app.services.report_writer import ReportWriter
router=APIRouter(prefix="/reports", tags=["reports"])
def _scan_dict(scan): return {"id":scan.id,"status":scan.status,"risk_score":scan.risk_score,"total_tests":scan.total_tests,"passed_tests":scan.passed_tests,"failed_tests":scan.failed_tests,"target_id":scan.target_id}
def _findings(db, scan_id): return [{k:v for k,v in r.__dict__.items() if not k.startswith("_")} for r in db.query(Finding).filter(Finding.scan_id==scan_id).all()]
def _ensure(scan_id, db):
    scan=db.get(Scan, scan_id)
    if not scan: raise HTTPException(status_code=404, detail="Scan not found")
    paths=ReportWriter().write_all(_scan_dict(scan), _findings(db,scan_id), scan_id)
    for fmt,key in {"json":"json_path","markdown":"markdown_path","html":"html_path","pdf":"pdf_path"}.items():
        if not db.query(Report).filter(Report.scan_id==scan_id, Report.format==fmt).first(): db.add(Report(scan_id=scan_id,format=fmt,path=paths[key]))
    db.commit(); return paths
@router.post("/{scan_id}/generate")
def generate_report(scan_id: str, db: Session = Depends(get_db)): return _ensure(scan_id, db)
@router.get("/{scan_id}/json")
def get_json(scan_id: str, db: Session = Depends(get_db)): return FileResponse(_ensure(scan_id,db)["json_path"], media_type="application/json")
@router.get("/{scan_id}/markdown")
def get_markdown(scan_id: str, db: Session = Depends(get_db)): return PlainTextResponse(Path(_ensure(scan_id,db)["markdown_path"]).read_text(encoding="utf-8"), media_type="text/markdown")
@router.get("/{scan_id}/html")
def get_html(scan_id: str, db: Session = Depends(get_db)): return FileResponse(_ensure(scan_id,db)["html_path"], media_type="text/html")
@router.get("/{scan_id}/pdf")
def get_pdf(scan_id: str, db: Session = Depends(get_db)): return FileResponse(_ensure(scan_id,db)["pdf_path"], media_type="application/pdf", filename=f"llmshield-{scan_id}.pdf")
