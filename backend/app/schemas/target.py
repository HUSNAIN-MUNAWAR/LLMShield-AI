from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TargetCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=160)
    type: str = "mock_llm"
    endpoint_url: str | None = None
    safe_mode: bool = False
    config: dict[str, Any] = Field(default_factory=dict)


class TargetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    endpoint_url: str | None
    safe_mode: bool
    config_json: str
    created_at: datetime
