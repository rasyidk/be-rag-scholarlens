import os
from datetime import datetime
from uuid import uuid4
from typing import Optional
from pathlib import Path

from app.db.mongodb import get_documents_collection
from app.utils.response import success_response, error_response
from bson import ObjectId
from pymongo import ReturnDocument


UPLOAD_DIR = Path("./uploads/documents")


def save_document(user_id: str, name: str, upload_file, project_id: Optional[str] = None):
    """Save uploaded PDF to disk and store metadata in MongoDB.

    upload_file is a Starlette UploadFile instance.
    """
    try:
        # Validate content type
        content_type = upload_file.content_type
        if content_type != "application/pdf":
            return error_response(message="Only PDF files are accepted", errors=[f"content_type={content_type}"], code=400)

        # Ensure upload dir exists
        dest_dir = UPLOAD_DIR / user_id
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Save file with uuid filename preserving extension
        ext = Path(upload_file.filename).suffix or ".pdf"
        saved_name = f"{uuid4().hex}{ext}"
        saved_path = dest_dir / saved_name

        # Write file to disk
        with open(saved_path, "wb") as fh:
            upload_file.file.seek(0)
            while True:
                chunk = upload_file.file.read(8192)
                if not chunk:
                    break
                fh.write(chunk)

        # Persist metadata
        docs = get_documents_collection()
        doc = {
            "project_id": project_id,
            "user_id": user_id,
            "name": name,
            "original_filename": upload_file.filename,
            "saved_filename": str(saved_path),
            "file_type": content_type,
            "text_content": "",
            "created_at": datetime.now(),
        }
        res = docs.insert_one(doc)
        doc["_id"] = str(res.inserted_id)

        return success_response(message="Document uploaded", data=doc, code=201)
    except Exception as e:
        return error_response(message="Failed to save document", errors=[str(e)], code=500)


def update_document(user_id: str, document_id: str, update_data: dict):
    """Partially update document metadata (name, project_id).

    Only the owner (user_id) can update the document.
    """
    docs = get_documents_collection()
    try:
        if not ObjectId.is_valid(document_id):
            return error_response(message="Invalid document id", errors=["document_id is not a valid ObjectId"], code=400)

        filter_q = {"_id": ObjectId(document_id), "user_id": user_id}
        update_q = {"$set": update_data}

        updated = docs.find_one_and_update(filter_q, update_q, return_document=ReturnDocument.AFTER)
        if not updated:
            return error_response(message="Document not found or not owned by user", errors=[], code=404)

        updated["_id"] = str(updated["_id"])
        return success_response(message="Document updated", data=updated, code=200)
    except Exception as e:
        return error_response(message="Failed to update document", errors=[str(e)], code=500)


def delete_document(user_id: str, document_id: str):
    """Delete a document owned by the given user. Also remove saved file from disk if present."""
    docs = get_documents_collection()
    try:
        if not ObjectId.is_valid(document_id):
            return error_response(message="Invalid document id", errors=["document_id is not a valid ObjectId"], code=400)

        # Ensure the document exists and belongs to user
        doc = docs.find_one({"_id": ObjectId(document_id), "user_id": user_id})
        if not doc:
            return error_response(message="Document not found or not owned by user", errors=[], code=404)

        # Attempt to remove the saved file from disk
        saved = doc.get("saved_filename")
        try:
            if saved:
                p = Path(saved)
                if p.exists():
                    p.unlink()
        except Exception:
            # Don't fail the delete if file removal fails; just proceed and return success
            pass

        result = docs.delete_one({"_id": ObjectId(document_id), "user_id": user_id})
        if result.deleted_count == 0:
            return error_response(message="Document not found or not owned by user", errors=[], code=404)

        return success_response(message="Document deleted", data={"_id": document_id}, code=200)
    except Exception as e:
        return error_response(message="Failed to delete document", errors=[str(e)], code=500)


def get_documents_by_project(user_id: str, project_id: str):
    """Return documents belonging to a project for a given user."""
    docs = get_documents_collection()
    try:
        pipeline = [
            {"$match": {"user_id": user_id, "project_id": project_id}},
            {"$addFields": {"_id": {"$toString": "$_id"}}},
        ]
        results = list(docs.aggregate(pipeline))
        return success_response(message="Documents fetched", data=results, code=200)
    except Exception as e:
        return error_response(message="Failed to fetch documents", errors=[str(e)], code=500)
