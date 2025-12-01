from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    # EmailStr requires the 'email-validator' package
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    # Includes password for creation
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(UserBase):
    # Excludes password_hash for security
    id: int
    created_at: datetime

    class Config:
        orm_mode = True 


class CalculationBase(BaseModel):
    operation: str = Field(..., description="Operation type: add, subtract, multiply, divide")
    operand_a: float = Field(..., description="First operand")
    operand_b: float = Field(..., description="Second operand")


class CalculationCreate(CalculationBase):
    pass


class CalculationRead(CalculationBase):
    id: int
    user_id: int
    result: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CalculationUpdate(BaseModel):
    operation: Optional[str] = Field(None, description="Operation type: add, subtract, multiply, divide")
    operand_a: Optional[float] = Field(None, description="First operand")
    operand_b: Optional[float] = Field(None, description="Second operand")
