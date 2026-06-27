from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScanCreate(BaseModel):
    target_id: str
    attack_pack_ids: list[str] = Field(default_factory=list)
    options: dict[str, Any] = Field(default_factory=dict)


class ScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    target_id: str
    status: str
    selected_packs_json: str
    options_json: str
    total_tests: int
    failed_tests: int
    passed_tests: int
    risk_score: float
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class ScanSummary(BaseModel):
    scan_id: str
    status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    risk_score: float
    severity_distribution: dict[str, int]
    category_distribution: dict[str, int]
