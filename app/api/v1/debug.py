from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import jwt
from app.core.security import decode_token
from app.core.config import get_settings
from datetime import datetime

router = APIRouter(prefix="/_debug", tags=["debug"])


@router.post("/token")
def inspect_token(authorization: str | None = Header(default=None)):
    """Return unverified header and payload for a provided Bearer token.

    WARNING: This endpoint does NOT verify signatures. Use only for local debugging and
    remove it from production.
    """
    if not authorization:
        return JSONResponse(content={"error": "Missing Authorization header"}, status_code=400)

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return JSONResponse(content={"error": "Expected 'Bearer <token>'"}, status_code=400)

    token = parts[1]
    try:
        header = jwt.get_unverified_header(token)
    except Exception as e:
        return JSONResponse(content={"error": "Invalid token header", "details": str(e)}, status_code=400)

    try:
        payload = jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        return JSONResponse(content={"error": "Failed to decode payload", "details": str(e)}, status_code=400)

    return JSONResponse(content=jsonable_encoder({"header": header, "payload": payload}), status_code=200)


@router.post("/verify")
def verify_token(authorization: str | None = Header(default=None)):
    """Attempt to verify the token signature and return server time vs token exp/iat.

    Useful to diagnose immediate-expiration issues.
    """
    if not authorization:
        return JSONResponse(content={"error": "Missing Authorization header"}, status_code=400)

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return JSONResponse(content={"error": "Expected 'Bearer <token>'"}, status_code=400)

    token = parts[1]
    # Get unverified payload to inspect exp/iat
    try:
        unverified = jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        return JSONResponse(content={"error": "Failed to decode payload", "details": str(e)}, status_code=400)

    settings = get_settings()
    server_time = datetime.utcnow().timestamp()

    # Try full verification
    try:
        payload = decode_token(token)
        return JSONResponse(content=jsonable_encoder({"status": "ok", "server_time": server_time, "payload": payload}), status_code=200)
    except jwt.ExpiredSignatureError:
        exp = unverified.get("exp")
        iat = unverified.get("iat")
        return JSONResponse(content=jsonable_encoder({
            "status": "error",
            "message": "Token expired",
            "server_time": server_time,
            "token_iat": iat,
            "token_exp": exp,
            "token_exp_readable": datetime.utcfromtimestamp(exp).isoformat() if exp else None,
            "token_iat_readable": datetime.utcfromtimestamp(iat).isoformat() if iat else None,
        }), status_code=401)
    except Exception as e:
        return JSONResponse(content=jsonable_encoder({"status": "error", "message": "Token invalid", "details": str(e), "server_time": server_time}), status_code=401)
