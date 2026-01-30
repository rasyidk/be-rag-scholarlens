from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
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


class UserModel(BaseModel):
    """MongoDB User document model."""
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: str
    password_hash: str
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    name: str
    email: EmailStr
    password: str
    email_verified: bool = False


class UserResponse(BaseModel):
    """Schema for user response (without password)."""
    
    id: str = Field(alias="_id")
    name: str
    email: str
    email_verified: bool
    created_at: datetime

    class Config:
        populate_by_name = True
