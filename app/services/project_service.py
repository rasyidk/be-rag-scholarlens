from datetime import datetime
from app.db.mongodb import get_projects_collection
from app.models.project import ProjectCreate
from app.utils.response import success_response, error_response
from bson import ObjectId
from pymongo import ReturnDocument


def create_project(user_id: str, project: ProjectCreate):
    """Create a new project for a user and return a standardized response."""
    projects = get_projects_collection()
    try:
        project_dict = project.dict()
        project_dict["user_id"] = user_id
        project_dict["created_at"] = datetime.now()

        result = projects.insert_one(project_dict)
        project_dict["_id"] = str(result.inserted_id)

        return success_response(
            message="Project created successfully",
            data=project_dict,
            code=201,
        )
    except Exception as e:
        return error_response(
            message="Failed to create project",
            errors=[str(e)],
            code=500,
        )


def get_projects(user_id: str):
    projects = get_projects_collection()
    try:
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$addFields": {"_id": {"$toString": "$_id"}}},
        ]
        docs = list(projects.aggregate(pipeline))

        return success_response(message="Projects fetched", data=docs, code=200)
    except Exception as e:
        return error_response(message="Failed to fetch projects", errors=[str(e)], code=500)


def update_project(user_id: str, project_id: str, update_data: dict):
    """Partially update a project for a user. Returns the updated document."""
    projects = get_projects_collection()
    try:
        if not ObjectId.is_valid(project_id):
            return error_response(message="Invalid project id", errors=["project_id is not a valid ObjectId"], code=400)

        filter_q = {"_id": ObjectId(project_id), "user_id": user_id}
        update_q = {"$set": update_data}

        updated = projects.find_one_and_update(filter_q, update_q, return_document=ReturnDocument.AFTER)
        if not updated:
            return error_response(message="Project not found or not owned by user", errors=[], code=404)

        # convert _id to string
        updated["_id"] = str(updated["_id"])
        return success_response(message="Project updated", data=updated, code=200)
    except Exception as e:
        return error_response(message="Failed to update project", errors=[str(e)], code=500)


def replace_project(user_id: str, project_id: str, new_data: dict):
    """Replace a project document for a user (PUT semantics)."""
    projects = get_projects_collection()
    try:
        if not ObjectId.is_valid(project_id):
            return error_response(message="Invalid project id", errors=["project_id is not a valid ObjectId"], code=400)

        filter_q = {"_id": ObjectId(project_id), "user_id": user_id}

        # Ensure user_id remains unchanged and set created_at unchanged (or update updated_at)
        new_data["user_id"] = user_id

        result = projects.replace_one(filter_q, new_data)
        if result.matched_count == 0:
            return error_response(message="Project not found or not owned by user", errors=[], code=404)

        updated = projects.find_one({"_id": ObjectId(project_id)})
        updated["_id"] = str(updated["_id"])
        return success_response(message="Project replaced", data=updated, code=200)
    except Exception as e:
        return error_response(message="Failed to replace project", errors=[str(e)], code=500)


def delete_project(user_id: str, project_id: str):
    """Delete a project owned by the given user."""
    projects = get_projects_collection()
    try:
        if not ObjectId.is_valid(project_id):
            return error_response(message="Invalid project id", errors=["project_id is not a valid ObjectId"], code=400)

        filter_q = {"_id": ObjectId(project_id), "user_id": user_id}
        result = projects.delete_one(filter_q)
        if result.deleted_count == 0:
            return error_response(message="Project not found or not owned by user", errors=[], code=404)

        return success_response(message="Project deleted", data={"_id": str(project_id)}, code=200)
    except Exception as e:
        return error_response(message="Failed to delete project", errors=[str(e)], code=500)
