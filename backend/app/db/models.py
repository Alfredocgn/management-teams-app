import uuid
from sqlalchemy import Column,String,ForeignKey,DateTime,Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base
from enum import Enum as PyEnum

class TaskStatus(PyEnum):
  pending = "pending"
  in_progress = "in_progress"
  completed = "completed"

class UserRole(PyEnum):
  admin = "admin"
  user = "user"

class SubscriptionStatus(PyEnum):
  active = "active"
  inactive = "expired"

class User(Base):
  __tablename__ = "users"
  id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
  first_name = Column(String)
  last_name = Column(String)
  email = Column(String,unique=True,index=True)
  password = Column(String)
  stripe_subscription = relationship("StripeSubscription",back_populates="user")


class ProjectUser(Base):
  __tablename__ = "project_user"
  project_id = Column(UUID(as_uuid=True),ForeignKey("projects.id"),primary_key=True)
  user_id = Column(UUID(as_uuid=True),ForeignKey("users.id"),primary_key=True)
  role = Column(String,default=UserRole.user.value)
  user = relationship("User")
  project = relationship("Project")

class Project(Base):
  __tablename__= "projects"
  id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
  title = Column(String)
  description = Column(String)
  tasks = relationship("Task",back_populates="project")
  


class Task(Base):
  __tablename__ = "tasks"
  id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
  title = Column(String)
  description = Column(String)
  status=Column(String,default=TaskStatus.pending.value)
  due_date = Column(DateTime)
  project_id = Column(UUID(as_uuid=True),ForeignKey("projects.id"))
  project = relationship("Project",back_populates="tasks") # a lo mejor esta relacion no es necesaria
  assignee_id = Column(UUID(as_uuid=True),ForeignKey("users.id")) # pueden ser varios usuarios (?) - seria many to many
  assignee = relationship("User")


class StripeSubscription(Base):
  __tablename__ = "stripe_subscriptions"
  id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
  user_id = Column(UUID(as_uuid=True),ForeignKey("users.id"))
  user = relationship("User",back_populates="stripe_subscription")
  subscription_id = Column(String)
  status = Column(String,default=SubscriptionStatus.inactive.value)
  current_period_start = Column(DateTime,nullable=True)