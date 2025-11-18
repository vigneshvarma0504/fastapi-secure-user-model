from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    # EmailStr requires the 'email-validator' package
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    # Includes password for creation
    password: str = Field(..., min_length=8)

class UserRead(UserBase):
    # Excludes password_hash for security
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 
