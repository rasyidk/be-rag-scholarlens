from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.models.project import ProjectCreate
from app.services.project_service import create_project as svc_create_project
from app.utils.response import success_response, error_response
from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("")
@router.post("/")
def create_project(project: ProjectCreate, user_id: str = Depends(get_current_user_id)):
    """Create a project for the authenticated user.

    Requires `Authorization: Bearer <token>` header containing a valid JWT.
    """
    svc_resp = svc_create_project(user_id, project)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 201))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))
