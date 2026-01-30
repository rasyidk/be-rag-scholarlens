from datetime import datetime
from typing import Optional, Literal
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


class ChatModel(BaseModel):
    """MongoDB Chat document model."""
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    project_id: PyObjectId
    role: Literal["user", "assistant"]
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ChatCreate(BaseModel):
    """Schema for creating a new chat message."""
    
    role: Literal["user", "assistant"]
    message: str


class ChatResponse(BaseModel):
    """Schema for chat response."""
    
    id: str = Field(alias="_id")
    project_id: str
    role: Literal["user", "assistant"]
    message: str
    created_at: datetime

    class Config:
        populate_by_name = True
