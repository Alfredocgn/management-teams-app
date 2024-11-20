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
  pass

class ProjectOut(ProjectBase):
  id:UUID
  owner_id:UUID
  team_members:List[UserOut]

  class Config:
    from_attributes = True
