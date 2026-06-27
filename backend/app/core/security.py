from __future__ import annotations
import base64, hashlib, hmac, json
from datetime import datetime, timedelta, timezone
from typing import Any
from app.core.config import settings
from app.core.redaction import redact_text
def redact(text: str | None) -> str: return redact_text(text)
def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest()[:16]).decode()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"pbkdf2_sha256${salt}${base64.urlsafe_b64encode(digest).decode()}"
def verify_password(password: str, password_hash: str) -> bool:
    try: _, salt, _ = password_hash.split("$", 2)
    except ValueError: return False
    return hmac.compare_digest(hash_password(password, salt), password_hash)
def _b64(data: bytes) -> str: return base64.urlsafe_b64encode(data).decode().rstrip("=")
def _unb64(data: str) -> bytes: return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))
def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    header = {"alg": settings.jwt_algorithm, "typ": "JWT"}
    exp = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or settings.access_token_minutes)
    payload = {"sub": subject, "role": role, "exp": int(exp.timestamp())}
    signing_input = f"{_b64(json.dumps(header,separators=(',',':')).encode())}.{_b64(json.dumps(payload,separators=(',',':')).encode())}"
    sig = hmac.new(settings.jwt_secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64(sig)}"
def decode_token(token: str) -> dict[str, Any]:
    try:
        h,p,s = token.split(".")
        expected = _b64(hmac.new(settings.jwt_secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(expected, s): raise ValueError("bad signature")
        payload = json.loads(_unb64(p))
        if int(payload.get("exp",0)) < int(datetime.now(timezone.utc).timestamp()): raise ValueError("expired")
        return payload
    except Exception as exc:
        raise ValueError("Invalid token") from exc

def decode_access_token(token: str) -> dict[str, Any]:
    return decode_token(token)


def create_refresh_token(subject: str, role: str) -> str:
    return create_access_token(subject, role, expires_minutes=settings.refresh_token_minutes)

def hash_api_key(api_key: str) -> str:
    return hmac.new(settings.jwt_secret.encode(), api_key.encode(), hashlib.sha256).hexdigest()

def verify_api_key(api_key: str, key_hash: str) -> bool:
    return hmac.compare_digest(hash_api_key(api_key), key_hash)

def generate_api_key() -> str:
    import secrets
    return f"{settings.api_key_prefix}_{secrets.token_urlsafe(32)}"
