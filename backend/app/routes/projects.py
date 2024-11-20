from fastapi import APIRouter, HTTPException,status, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from config.security import get_current_user
from db.models import User
from schemas.project_schema import ProjectCreate,ProjectOut,ProjectUpdate
from schemas.user_schema import UserOut
from db.models import Project
from typing import List
from uuid import UUID


router = APIRouter()

@router.post('/projects',response_model = ProjectOut,tags=['projects'])
async def create_project(project:ProjectCreate, current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  if not current_user.is_subscribed:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User is not subscribed")
  
  new_project = Project(**project.model_dump(),owner_id=current_user.id)
  db.add(new_project)
  db.commit()
  db.refresh(new_project)
  return new_project


@router.get('/projects',response_model = List[ProjectOut], tags=['projects'])
async def get_projects(current_user: User= Depends(get_current_user),db:Session=Depends(get_db)):
  projects = db.query(Project).filter((Project.owner_id == current_user.id) | (Project.team_members.any(id=current_user.id))).all()
  return projects

@router.get('/projects/{project_id}',response_model=ProjectOut,tags=['projects'])
async def get_project(project_id:UUID,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  project = db.query(Project).filter(Project.id == project_id).first()
  if not project:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Project not found")
  if project.owner_id != current_user.id and current_user.id not in [m.id for m in project.team_members]:
    raise HTTPException(status_code = status.HTTP_403_FORBIDDEN,detail="Not authorized to access this project")
  return project

@router.put('/projects/{project_id}',response_model=ProjectOut,tags=["projects"])
async def update_project(project_id:UUID,project_update:ProjectUpdate,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  project:ProjectOut = await get_project(project_id,current_user,db)
  if project.owner_id  != current_user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Only project owner can update the project')

  project.title = project_update.title
  project.description = project_update.description
  db.commit()
  db.refresh(project)
  return project


@router.delete('/projects/{project_id}',tags=["projects"])
async def delete_project(
  project_id:UUID,
  current_user:User = Depends(get_current_user),
  db:Session = Depends(get_db)
):
  project:ProjectOut = await get_project(project_id,current_user,db)
  if project.owner_id  != current_user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail='Only project owner can delete the project')

  db.delete(project)
  db.commit()
  return{"message":"Project deleted successfully"}


@router.post('/projects/{project_id}/members/{user_id}',response_model=ProjectOut,tags=["projects"])
async def add_team_member(
  project_id:UUID,
  user_id:UUID,
  current_user:User=Depends(get_current_user),
  db:Session=Depends(get_db)
):
  project = await get_project(project_id,current_user,db)
  if project.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only project owner can add team members")
  user = db.query(User).filter(User.id == user_id).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='User not found')
  
  project.team_members.append(user)
  db.commit()
  db.refresh(project)
  return project

@router.delete('/projects/{project_id}/members/{user_id}',response_model=ProjectOut,tags=["projects"])
async def remove_team_member(project_id:UUID,user_id:UUID,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  project = await get_project(project_id,current_user,db)
  if project.owner_id != current_user.id:
    raise HTTPException(satus_code= status.HTTP_403_FORBIDDEN,detail="Only project owner can remove team members")
  user = db.query(User).filter(User.id == user_id).first()
  if not user:
    raise HTTPException(
      status_code = status.HTTP_404_NOT_FOUND,
      detail = "User not found"
    )
  if user.id not in [m.id for m in project.team_members]:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detaul="User is not a team member")

  project.team_members.remove(user)
  db.commit()
  db.refresh(project)
  return project


@router.get('/projects/{project_id}/members',response_model=List[UserOut])
async def get_project_members(project_id:UUID,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  project = await get_project(project_id,current_user,db)
  return project.team_members