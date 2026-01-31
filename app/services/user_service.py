
from app.db.mongodb import get_users_collection
from app.models.user import UserCreate, UserModel, UserResponse
from fastapi import HTTPException
from datetime import datetime
from passlib.hash import argon2
from app.utils.response import success_response, error_response

def get_password_hash(password: str) -> str:
    return argon2.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return argon2.verify(password, hashed)
 

def create_user(user: UserCreate):
    """Create a new user in the database and return a standardized response."""
    users = get_users_collection()
    if users.find_one({"email": user.email}):
        return error_response(
            message="Email already registered",
            errors=["User with this email already exists"],
            code=400
        )
    try:
        user_dict = user.dict()
        user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
        user_dict["created_at"] = datetime.utcnow()
        user_dict["email_verified"] = True
        result = users.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        user_response = UserResponse(**user_dict)
        return success_response(
            message="User created successfully",
            data=user_response.dict(by_alias=True),
            code=201
        )
    except Exception as e:
        return error_response(
            message="Failed to create user",
            errors=[str(e)],
            code=500
        )


def set_email_verified(email: str):
    """Mark a user's email as verified and return a standardized response."""
    users = get_users_collection()
    try:
        result = users.update_one({"email": email}, {"$set": {"email_verified": True}})
        if result.modified_count > 0:
            return success_response(
                message="Email verified successfully",
                data=None,
                code=200
            )
        else:
            return error_response(
                message="Email not found or already verified",
                errors=["No user found with this email or already verified"],
                code=404
            )
    except Exception as e:
        return error_response(
            message="Failed to verify email",
            errors=[str(e)],
            code=500
        )


def authenticate_user(email: str, password: str):
    """Verify user credentials and return standardized response."""
    users = get_users_collection()
    try:
        user_doc = users.find_one({"email": email})
        if not user_doc:
            return error_response(
                message="User not found",
                errors=[f"User with email {email} does not exist"],
                code=404,
            )

        # Verify password
        hashed = user_doc.get("password_hash")
        if not hashed or not verify_password(password, hashed):
            return error_response(
                message="Invalid credentials",
                errors=["Email or password is incorrect"],
                code=401,
            )

        # Build response without password
        user_doc["_id"] = str(user_doc.get("_id"))
        # Use UserResponse to filter fields
        user_response = UserResponse(**user_doc)
        # create JWTs
        try:
            from app.core.security import create_access_token, create_refresh_token

            access_token, access_expires = create_access_token(user_response.id)
            refresh_token, refresh_expires = create_refresh_token(user_response.id)
            token_payload = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": access_expires,
            }
        except Exception:
            # If token creation fails, still return authenticated user but indicate no tokens
            token_payload = None

        data = {"user": user_response.dict(by_alias=True)}
        if token_payload:
            data.update(token_payload)

        return success_response(
            message="Authenticated successfully",
            data=data,
            code=200,
        )
    except Exception as e:
        return error_response(
            message="Authentication failed",
            errors=[str(e)],
            code=500,
        )


def logout(refresh_token: str):
    """Revoke a refresh token by adding its JTI to the blacklist with expiry."""
    try:
        from app.core.security import decode_token
        from app.db.mongodb import get_blacklist_collection
        from jwt import InvalidTokenError

        payload = decode_token(refresh_token)
        # Only process refresh tokens
        if payload.get("type") != "refresh":
            return error_response(
                message="Provided token is not a refresh token",
                errors=["Token type invalid"],
                code=400,
            )

        jti = payload.get("jti")
        exp_ts = payload.get("exp")
        if not jti or not exp_ts:
            return error_response(
                message="Token missing required claims",
                errors=["jti or exp claim missing"],
                code=400,
            )

        expires_at = datetime.utcfromtimestamp(int(exp_ts))
        blacklist = get_blacklist_collection()
        # Insert blacklist record; if duplicate, ignore
        try:
            blacklist.insert_one({"jti": jti, "expires_at": expires_at})
        except Exception:
            # If insertion fails (e.g., duplicate key), just continue
            pass

        return success_response(
            message="Logged out successfully",
            data=None,
            code=200,
        )
    except InvalidTokenError as e:
        return error_response(
            message="Invalid token",
            errors=[str(e)],
            code=401,
        )
    except Exception as e:
        return error_response(
            message="Failed to logout",
            errors=[str(e)],
            code=500,
        )
