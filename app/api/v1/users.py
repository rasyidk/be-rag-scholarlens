from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.models.user import UserCreate, LoginRequest, LogoutRequest
from app.services.user_service import create_user, set_email_verified, authenticate_user
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/users", tags=["users"])

def send_verification_email(email: str):
    print(f"Send verification email to {email}")


@router.post("/signup")
def signup(user: UserCreate, background_tasks: BackgroundTasks):
    user_resp = create_user(user)
    if user_resp.get("status") == "success" and user_resp.get("data"):
        background_tasks.add_task(send_verification_email, user_resp["data"]["email"])
        resp = success_response(message=user_resp.get("message"), data=user_resp.get("data"), code=user_resp.get("code", 200))
    else:
        resp = error_response(message=user_resp.get("message"), errors=user_resp.get("errors", []), code=user_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.post("/verify-email")
def verify_email(email: str):
    svc_resp = set_email_verified(email)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.post("/login")
def login(payload: LoginRequest):
    svc_resp = authenticate_user(payload.email, payload.password)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.post("/logout")
def logout(payload: LogoutRequest):
    svc_resp = None
    try:
        from app.services.user_service import logout as svc_logout
        svc_resp = svc_logout(payload.refresh_token)
    except Exception as e:
        svc_resp = error_response(message="Logout failed", errors=[str(e)], code=500)

    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))
