from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.utils.response import success_response, error_response
from app.core.dependencies import get_current_user_id
from app.services.document_service import save_document
from app.services.document_service import update_document as svc_update_document
from app.models.document import DocumentUpdate
from app.services.document_service import delete_document as svc_delete_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("")
def upload_document(
    name: str = Form(...),
    file: UploadFile = File(...),
    project_id: str | None = Form(default=None),
    user_id: str = Depends(get_current_user_id),
):
    """Upload a PDF document with a name and optional project association."""
    svc_resp = save_document(user_id, name, file, project_id)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 201))
        return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 201))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
        return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 400))


@router.patch("/{document_id}")
def patch_document(document_id: str, payload: DocumentUpdate, user_id: str = Depends(get_current_user_id)):
    """Update document metadata (name, project_id)."""
    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        resp = error_response(message="No update data provided", errors=[], code=400)
        return JSONResponse(content=jsonable_encoder(resp), status_code=400)

    svc_resp = svc_update_document(user_id, document_id, update_data)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))


@router.delete("/{document_id}")
def delete_doc(document_id: str, user_id: str = Depends(get_current_user_id)):
    """Delete a document by id (must belong to authenticated user)."""
    svc_resp = svc_delete_document(user_id, document_id)
    if svc_resp.get("status") == "success":
        resp = success_response(message=svc_resp.get("message"), data=svc_resp.get("data"), code=svc_resp.get("code", 200))
    else:
        resp = error_response(message=svc_resp.get("message"), errors=svc_resp.get("errors", []), code=svc_resp.get("code", 400))
    return JSONResponse(content=jsonable_encoder(resp), status_code=resp.get("code", 200))
