from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from app.core.config import settings
from app.services.scan_queue import create_status, update_status

@dataclass
class QueueResult:
    job_id: str
    queued: bool
    backend: str
    message: str

def enqueue_scan(scan_id: str) -> QueueResult:
    job_id=f"scan-{scan_id[:8]}"
    create_status(scan_id, job_id)
    try:
        from redis import Redis  # type: ignore
        from rq import Queue  # type: ignore
        q=Queue("llmshield-scans", connection=Redis.from_url(settings.redis_url))
        job=q.enqueue("app.workers.tasks.execute_scan_job", scan_id, job_timeout=max(60, settings.scan_timeout_seconds * 4))
        update_status(scan_id,status="queued",progress=0)
        return QueueResult(job_id=job.id, queued=True, backend="rq", message="Queued in Redis/RQ")
    except Exception as exc:
        update_status(scan_id,status="queued",progress=0,error_message=f"RQ unavailable: {str(exc)[:120]}")
        return QueueResult(job_id=job_id, queued=False, backend="memory-fallback", message=f"RQ unavailable; local fallback can execute synchronously: {str(exc)[:120]}")
