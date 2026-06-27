from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.finding import Finding
from app.schemas.finding import FindingRead

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("", response_model=list[FindingRead])
def list_findings(db: Session = Depends(get_db)) -> list[Finding]:
    return list(db.query(Finding).order_by(Finding.created_at.desc()).limit(200).all())


@router.get("/{finding_id}", response_model=FindingRead)
def get_finding(finding_id: str, db: Session = Depends(get_db)) -> Finding:
    finding = db.get(Finding, finding_id)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding
