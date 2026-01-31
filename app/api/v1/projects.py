from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.models.project import ProjectCreate
from app.services.project_service import create_project as svc_create_project, get_projects as svc_get_projects
from app.services.project_service import update_project as svc_update_project, replace_project as svc_replace_project
from app.services.project_service import delete_project as svc_delete_project
from app.services.document_service import get_documents_by_project as svc_get_documents_by_project
from app.models.project import ProjectUpdate
from app.utils.response import success_response, error_response
from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("")
def create_project(project: ProjectCreate, user_id: str = Depends(get_current_user_id)):
    svc_resp = svc_create_project(user_id, project)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 201))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.get("")
def list_projects(user_id: str = Depends(get_current_user_id)):
    svc_resp = svc_get_projects(user_id)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.patch("/{project_id}")
def patch_project(project_id: str, payload: ProjectUpdate, user_id: str = Depends(get_current_user_id)):
    """Partially update a project (PATCH)."""
    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        resp = error_response(message="No data provided for update", errors=[], code=400)
        return JSONResponse(content=jsonable_encoder(resp), status_code=400)

    svc_resp = svc_update_project(user_id, project_id, update_data)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.put("/{project_id}")
def put_project(project_id: str, payload: ProjectCreate, user_id: str = Depends(get_current_user_id)):
    """Replace a project (PUT)."""
    # Use the create schema to ensure required fields exist
    new_data = payload.dict()
    new_data["created_at"] = new_data.get("created_at") or None

    svc_resp = svc_replace_project(user_id, project_id, new_data)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.delete("/{project_id}")
def delete_project(project_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete a project by id (must belong to authenticated user)."""
    svc_resp = svc_delete_project(user_id, project_id)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.get("/{project_id}/documents")
def project_documents(project_id: str, user_id: str = Depends(get_current_user_id)):
    """Return documents that belong to a project for the authenticated user."""
    svc_resp = svc_get_documents_by_project(user_id, project_id)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))



