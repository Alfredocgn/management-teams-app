from pydantic import BaseModel, EmailStr,field_validator
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
  email: EmailStr
  first_name: str
  last_name: str


class UserCreate(UserBase):
  password: str 
  @field_validator('password')
  def validate_password(cls, v):
    if not any(char.isdigit() for char in v):
        raise ValueError('Password must contain at least one number')
    if not any(char.isupper() for char in v):
        raise ValueError('Password must contain at least one uppercase letter')
    return v

class UserUpdate(BaseModel):
  email: EmailStr | None = None
  password: str | None = None
  first_name: str | None = None
  last_name: str | None = None
  @field_validator('password')
  def validate_password(cls, v):
    if not any(char.isdigit() for char in v):
        raise ValueError('Password must contain at least one number')
    if not any(char.isupper() for char in v):
        raise ValueError('Password must contain at least one uppercase letter')
    return v

class UserOut(UserBase):
  id: UUID

  class Config:
    from_attributes = True