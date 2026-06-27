from __future__ import annotations
from pydantic import BaseModel, Field

class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    scoped_role: str = "ci_runner"
    notes: str | None = None

class ApiKeyCreated(BaseModel):
    id: str
    name: str
    key_prefix: str
    scoped_role: str
    api_key: str
    message: str = "Store this key now. It is shown only once."

class ApiKeyRead(BaseModel):
    id: str
    name: str
    key_prefix: str
    scoped_role: str
    is_active: bool
    created_at: str | None = None
    last_used_at: str | None = None
    revoked_at: str | None = None
