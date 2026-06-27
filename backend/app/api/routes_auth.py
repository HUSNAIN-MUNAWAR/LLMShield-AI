from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, RefreshRequest, TokenResponse
from app.services.audit_logger import audit
router=APIRouter(prefix="/auth", tags=["auth"])
def ensure_demo_users(db: Session):
    for email,name,role,pw in [("admin@llmshield.local","Admin Demo","admin","admin123"),("analyst@llmshield.local","Analyst Demo","analyst","analyst123"),("viewer@llmshield.local","Viewer Demo","viewer","viewer123")]:
        if not db.query(User).filter(User.email==email).first():
            db.add(User(email=email,name=name,role=role,password_hash=hash_password(pw)))
    db.commit()
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    ensure_demo_users(db); user=db.query(User).filter(User.email==payload.email).first()
    if not user or not verify_password(payload.password,user.password_hash):
        audit(db,"login_failed",status="failed",detail={"email":payload.email}); raise HTTPException(status_code=401, detail="Invalid credentials")
    token=create_access_token(user.id,user.role); refresh=create_refresh_token(user.id,user.role); audit(db,"login",actor=user,detail={"role":user.role})
    return TokenResponse(access_token=token,refresh_token=refresh,user={"id":user.id,"email":user.email,"name":user.name,"role":user.role})
@router.post("/demo-login", response_model=TokenResponse)
def demo_login(role: str = "analyst", db: Session = Depends(get_db)):
    ensure_demo_users(db); role=role if role in {"admin","analyst","viewer"} else "analyst"; user=db.query(User).filter(User.email==f"{role}@llmshield.local").first()
    token=create_access_token(user.id,user.role); refresh=create_refresh_token(user.id,user.role); audit(db,"demo_login",actor=user,detail={"role":user.role})
    return TokenResponse(access_token=token,refresh_token=refresh,user={"id":user.id,"email":user.email,"name":user.name,"role":user.role})
@router.get("/me")
def me(user: User = Depends(get_current_user)): return {"id":user.id,"email":user.email,"name":user.name,"role":user.role}
@router.post("/logout")
def logout(): return {"status":"ok","message":"Client should discard the bearer token."}

@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        token_payload = decode_token(payload.refresh_token)
    except ValueError as exc:
        audit(db,"refresh_failed",status="failed"); raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    user=db.get(User, token_payload.get("sub"))
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Inactive or missing user")
    token=create_access_token(user.id,user.role); refresh_token=create_refresh_token(user.id,user.role); audit(db,"refresh",actor=user)
    return TokenResponse(access_token=token,refresh_token=refresh_token,user={"id":user.id,"email":user.email,"name":user.name,"role":user.role})

@router.post("/change-password")
def change_password(payload: ChangePasswordRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        audit(db,"change_password_failed",actor=user,status="failed"); raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(payload.new_password) < 8: raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    user.password_hash=hash_password(payload.new_password); db.commit(); audit(db,"change_password",actor=user)
    return {"status":"ok"}
