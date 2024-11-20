import uuid
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,DateTime,Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from enum import Enum as PyEnum

class TaskStatus(PyEnum):
  pending = "pending"
  in_progress = "in_progress"
  completed = "completed"


user_project = Table('user_project',Base.metadata,
                      Column('user_id',UUID(as_uuid=True),ForeignKey('users.id'),primary_key=True),
                      Column('project_id',UUID(as_uuid=True),ForeignKey('projects.id'),primary_key=True))

class User(Base):
  __tablename__ = "users"
  id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
  email = Column(String,unique=True,index=True)
  hashed_password = Column(String)
  is_subscribed = Column(Boolean,default=False)
  subscription_end = Column(DateTime)
  owned_projects = relationship("Project",back_populates="owner")
  team_projects = relationship("Project",secondary=user_project,back_populates="team_members")


class Project(Base):
  __tablename__ = "projects"
  id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
  title = Column(String)
  owner_id = Column(UUID(as_uuid=True),ForeignKey('users.id'))
  owner = relationship("User",back_populates="owned_projects")
  tasks = relationship("Task",back_populates="project")
  team_members = relationship("User",secondary=user_project,back_populates="team_projects")


class Task(Base):
  __tablename__ = "tasks"
  id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
  description = Column(String)
  status=Column(String,default=TaskStatus.pending)
  project_id = Column(UUID(as_uuid=True),ForeignKey("projects.id"))
  project = relationship("Project",back_populates="tasks")
