from __future__ import annotations
from datetime import datetime, timezone
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token, hash_api_key
from app.models.api_key import ApiKey
from app.models.user import User

ROLE_ORDER={"viewer":1,"ci_runner":2,"analyst":3,"admin":4}

def _api_key_user(api_key: str, db: Session) -> User | None:
    key_hash = hash_api_key(api_key)
    row=db.query(ApiKey).filter(ApiKey.key_hash==key_hash, ApiKey.is_active==True).first()
    if not row: return None
    row.last_used_at=datetime.now(timezone.utc); db.commit()
    # synthetic user object for dependency checks; not persisted.
    return User(id=row.owner_user_id or row.id, email=f"api-key:{row.key_prefix}@llmshield.local", name=row.name, role=row.scoped_role, password_hash="api-key")

def get_current_user(authorization: str | None = Header(default=None), x_llmshield_api_key: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if x_llmshield_api_key:
        user=_api_key_user(x_llmshield_api_key, db)
        if user: return user
        raise HTTPException(status_code=401, detail="Invalid API key")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ",1)[1]
    # Allow API keys in Authorization: Bearer for CI clients.
    if token.startswith("lsk_"):
        user=_api_key_user(token, db)
        if user: return user
        raise HTTPException(status_code=401, detail="Invalid API key")
    try: payload=decode_token(token)
    except ValueError as exc: raise HTTPException(status_code=401, detail="Invalid token") from exc
    user=db.get(User, payload.get("sub"))
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Inactive or missing user")
    return user

def require_role(role: str):
    def _dep(user: User = Depends(get_current_user)) -> User:
        if ROLE_ORDER.get(user.role,0)<ROLE_ORDER[role]: raise HTTPException(status_code=403, detail=f"Requires {role} role")
        return user
    return _dep
