from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    # Includes password for creation
    password: str = Field(..., min_length=8)

class UserRead(UserBase):
    # Excludes password_hash
    id: int
    created_at: datetime

    class Config:
        # Pydantic models must be configured to work with SQLAlchemy ORM
        orm_mode = True 
