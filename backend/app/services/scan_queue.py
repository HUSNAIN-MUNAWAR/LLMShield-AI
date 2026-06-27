from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
@dataclass
class ScanStatus:
    scan_id: str
    job_id: str
    status: str = "queued"
    progress: int = 0
    current_test: str | None = None
    error_message: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
_STATUS: dict[str, ScanStatus]={}; _CANCELLED:set[str]=set()
def create_status(scan_id: str, job_id: str):
    row=ScanStatus(scan_id,job_id); _STATUS[scan_id]=row; return row
def update_status(scan_id: str, **kwargs):
    row=_STATUS.setdefault(scan_id, ScanStatus(scan_id, scan_id))
    for k,v in kwargs.items(): setattr(row,k,v)
    return row
def get_status(scan_id: str): return _STATUS.setdefault(scan_id, ScanStatus(scan_id, scan_id))
def cancel_scan(scan_id: str): _CANCELLED.add(scan_id); update_status(scan_id,status="cancelled",completed_at=datetime.now(timezone.utc).isoformat())
def is_cancelled(scan_id: str): return scan_id in _CANCELLED
