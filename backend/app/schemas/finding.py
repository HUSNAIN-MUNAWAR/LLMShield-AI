from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scan_id: str
    attack_pack_id: str
    test_id: str
    test_name: str
    prompt: str
    response: str
    detector_name: str
    passed: bool
    severity: str
    risk_score: int
    category: str
    mitre_tactic: str
    confidence: float
    evidence: str
    mitigation: str
    latency_ms: int
    token_estimate: int
    created_at: datetime
