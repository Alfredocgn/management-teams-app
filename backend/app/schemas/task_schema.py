from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from schemas.user_schema import UserOut
from typing import Optional


class TaskBase(BaseModel):
  title:str
  description:str
  due_date:datetime
  assignee_id: Optional[UUID] = None

class TaskCreate(TaskBase):
  pass

class TaskUpdate(BaseModel):
  title: Optional[str] = None
  description: Optional[str] = None
  due_date: Optional[datetime] = None
  assignee_id: Optional[UUID] = None
  status: Optional[str] = None

class TaskOut(TaskBase):
  id:UUID
  project_id:UUID
  status:str
  assignee:Optional[UserOut] = None

  class Config:
    from_attributes = True