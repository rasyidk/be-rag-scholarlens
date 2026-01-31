from fastapi import Header, HTTPException
import jwt
import logging
from fastapi import Request
from app.core.security import decode_token
from app.utils.response import error_response

logger = logging.getLogger(__name__)


def get_current_user_id(authorization: str | None = Header(default=None)) -> str:
    """Dependency to extract and validate JWT from Authorization header.

    Returns the user id (from `sub` claim) or raises HTTPException(401).
    """
    if not authorization:
        detail = error_response(message="Authorization header missing", errors=["Missing Authorization header"], code=401)
        raise HTTPException(status_code=401, detail=detail)

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        detail = error_response(message="Invalid authorization header", errors=["Expected 'Bearer <token>'"], code=401)
        raise HTTPException(status_code=401, detail=detail)

    token = parts[1]
    try:
        payload = decode_token(token)
        user_id = payload.get("sub") or payload.get("uid")
        if not user_id:
            detail = error_response(message="Token missing subject", errors=["Token does not contain user id"], code=401)
            raise HTTPException(status_code=401, detail=detail)
        return user_id
    except Exception as e:
        # Add detailed debug logging for development to trace why verification failed
        err_msg = str(e)
        try:
            # Attempt to get unverified payload for timestamps to help diagnose expiry
            unverified = jwt.decode(token, options={"verify_signature": False})
            iat = unverified.get("iat")
            exp = unverified.get("exp")
        except Exception:
            iat = None
            exp = None

        server_time = None
        try:
            import time

            server_time = time.time()
        except Exception:
            server_time = None

        logger.warning(
            "JWT verification failed: %s; server_time=%s token_iat=%s token_exp=%s",
            err_msg,
            server_time,
            iat,
            exp,
        )

        # Provide clearer client-facing messages for common JWT exceptions
        if isinstance(e, jwt.ExpiredSignatureError):
            detail = error_response(message="Token expired", errors=[str(e)], code=401)
        elif isinstance(e, (jwt.InvalidSignatureError, jwt.exceptions.InvalidSignatureError)):
            detail = error_response(
                message="Signature verification failed",
                errors=["Token signature invalid. Check that the token was not altered and that the server's JWT_SECRET_KEY and JWT_ALGORITHM match the issuer."],
                code=401,
            )
        else:
            detail = error_response(message="Invalid or expired token", errors=[err_msg], code=401)

        raise HTTPException(status_code=401, detail=detail)
