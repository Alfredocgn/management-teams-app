from pydantic import BaseModel
from uuid import UUID
from db.models import UserRole

class ProjectUserBase(BaseModel):
  project_id:UUID
  user_id:UUID
  role:UserRole

class ProjectUserCreate(ProjectUserBase):
  pass

class ProjectUserUpdate(ProjectUserBase):
  pass

class ProjectUserOut(ProjectUserBase):
  id:UUID
  class Config:
    from_attributes = True

