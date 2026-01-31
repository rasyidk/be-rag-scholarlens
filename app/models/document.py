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


class DocumentModel(BaseModel):
    """MongoDB Document document model."""
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    project_id: Optional[PyObjectId] = None
    filename: str
    file_type: str
    text_content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DocumentCreate(BaseModel):
    """Schema for creating a new document."""
    
    filename: str
    file_type: str
    text_content: str


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata (partial)."""
    name: Optional[str] = None
    project_id: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document response."""
    
    id: str = Field(alias="_id")
    project_id: str
    filename: str
    file_type: str
    text_content: str
    created_at: datetime

    class Config:
        populate_by_name = True
