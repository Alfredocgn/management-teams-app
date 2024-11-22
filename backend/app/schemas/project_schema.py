from pydantic import BaseModel
from uuid import UUID
from typing import List
from schemas.user_schema import UserOut

class ProjectBase(BaseModel):
  title:str
  description:str

class ProjectCreate(ProjectBase):
  pass

class ProjectUpdate(ProjectBase):
  title: str | None = None
  description: str | None = None

class ProjectOut(ProjectBase):
  id:UUID

  class Config:
    from_attributes = True

class ProjectDetailOut(ProjectOut):
    team_members: List[UserOut] = [] 
    
    class Config:
        from_attributes = True