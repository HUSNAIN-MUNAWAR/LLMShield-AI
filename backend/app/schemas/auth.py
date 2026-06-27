from __future__ import annotations
from pydantic import BaseModel
class LoginRequest(BaseModel):
    email: str
    password: str
class RefreshRequest(BaseModel):
    refresh_token: str
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user: dict
