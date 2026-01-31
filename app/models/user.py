from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, constr
from bson import ObjectId


class PyObjectId(str):
    
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

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    email: str
    password_hash: str
    email_verified: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    name: str
    email: EmailStr
    password: constr(min_length=8)
    email_verified: bool = True
    
    @classmethod
    def validate_password(cls, value):
        import re
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise ValueError('Password must contain at least one symbol')
        return value

    # For Pydantic v1
    from pydantic import validator
    @validator('password')
    def password_complexity(cls, v):
        return cls.validate_password(v)


class UserResponse(BaseModel):
    
    id: str = Field(alias="_id")
    name: str
    email: str
    email_verified: bool
    created_at: datetime

    class Config:
        populate_by_name = True


class LoginRequest(BaseModel):
  
    email: EmailStr
    password: constr(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str
