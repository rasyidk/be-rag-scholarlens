from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    """Custom type for handling MongoDB ObjectId."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")


class ProjectModel(BaseModel):
    """MongoDB Project document model."""
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    
    id: str = Field(alias="_id")
    user_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        populate_by_name = True
