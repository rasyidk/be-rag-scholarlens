from datetime import datetime
from app.db.mongodb import get_projects_collection
from app.models.project import ProjectCreate
from app.utils.response import success_response, error_response


def create_project(user_id: str, project: ProjectCreate):
    """Create a new project for a user and return a standardized response."""
    projects = get_projects_collection()
    try:
        project_dict = project.dict()
        project_dict["user_id"] = user_id
        project_dict["created_at"] = datetime.utcnow()

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
