from pydantic import BaseModel, Field, EmailStr
from beanie import Document
from uuid import uuid4, UUID
from typing import Optional
from datetime import datetime


class UserSignUp(BaseModel):
    user_name: str
    phone_number: str = Field(..., example="+919876543210")
    full_name : Optional[str] = None
    email : Optional[str] = None

class UserSignIn(BaseModel):
    phone_number: str = Field(...)

class UserOut(BaseModel):
    uuid: UUID
    user_name: str
    phone_number: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class User(Document):
    uuid : UUID = Field(default_factory=uuid4, unique=True)
    user_name: str = Field(..., unique=True)
    phone_number: str = Field(..., example="+91XXXXXXXXXX")
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "Users"
        
