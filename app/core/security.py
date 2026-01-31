import jwt
import base64
from datetime import datetime, timedelta
from typing import Tuple
from uuid import uuid4
from app.core.config import get_settings


settings = get_settings()


def _now_utc() -> datetime:
    return datetime.utcnow()


def create_access_token(subject: str, expires_minutes: int = None) -> Tuple[str, int]:
    """Create a JWT access token.

    Returns tuple (token, expires_in_seconds).
    """
    print(subject)
    if expires_minutes is None:
        expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    now = _now_utc()
    exp = now + timedelta(minutes=expires_minutes)
    jti = str(uuid4())
    # Encode the user id to include in the token (URL-safe base64)
    try:
        uid_bytes = str(subject).encode()
        uid_encoded = base64.urlsafe_b64encode(uid_bytes).decode()
    except Exception:
        uid_encoded = str(subject)

    payload = {
        "sub": str(subject),
        "uid": uid_encoded,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
        "type": "access",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_minutes * 60


def create_refresh_token(subject: str, expires_days: int = None) -> Tuple[str, int]:
    """Create a JWT refresh token.

    Returns tuple (token, expires_in_seconds).
    """
    if expires_days is None:
        expires_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    now = _now_utc()
    exp = now + timedelta(days=expires_days)
    jti = str(uuid4())
    # Encode the user id to include in the token (URL-safe base64)
    try:
        uid_bytes = str(subject).encode()
        uid_encoded = base64.urlsafe_b64encode(uid_bytes).decode()
    except Exception:
        uid_encoded = str(subject)

    payload = {
        "sub": str(subject),
        "uid": uid_encoded,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
        "type": "refresh",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, expires_days * 24 * 3600


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token. Raises jwt exceptions on failure."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
