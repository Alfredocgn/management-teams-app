from fastapi import APIRouter, HTTPException,status, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from config.security import get_current_user
from db.models import User
from schemas.project_schema import ProjectCreate,ProjectOut,ProjectUpdate
from schemas.user_schema import UserOut
from schemas.project_user_schema import ProjectUserCreate
from db.models import Project,ProjectUser,UserRole
from typing import List
from uuid import UUID


router = APIRouter()

@router.post('/projects',response_model = ProjectOut,tags=['projects'])
async def create_project(project:ProjectCreate, current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if not current_user.stripe_subscription:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User is not subscribed")
    new_project = Project(**project.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    new_project_user = ProjectUser(project_id=new_project.id,user_id=current_user.id,role= UserRole.admin.value)
    db.add(new_project_user)
    db.commit()
    db.refresh(new_project_user)
    return new_project


@router.get('/projects',response_model = List[ProjectOut], tags=['projects'])
async def get_projects(current_user: User= Depends(get_current_user),db:Session=Depends(get_db)):
    project_users = db.query(ProjectUser).filter((ProjectUser.user_id == current_user.id)).all()
    projects = [pu.project for pu in project_users]
    return projects

@router.get('/projects/{project_id}', response_model=ProjectOut, tags=['projects'])
async def get_project(project_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    project_user = db.query(ProjectUser).filter(
        ProjectUser.project_id == project_id,
        ProjectUser.user_id == current_user.id
    ).first()
    
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return project_user.project

@router.put('/projects/{project_id}', response_model=ProjectOut, tags=["projects"])
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project_user = db.query(ProjectUser).filter(
        ProjectUser.project_id == project_id,
        ProjectUser.user_id == current_user.id,
        ProjectUser.role == UserRole.admin.value
    ).first()
    
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only project admin can update the project'
        )

    project = project_user.project
    for key, value in project_update.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project



@router.delete('/projects/{project_id}', tags=["projects"])
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    project_user = db.query(ProjectUser).filter(
        ProjectUser.project_id == project_id,
        ProjectUser.user_id == current_user.id,
        ProjectUser.role == UserRole.admin.value
    ).first()
    
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only project admin can delete the project'
        )

    project = project_user.project
    db.delete(project) 
    db.commit()
    return {"message": "Project deleted successfully"}


@router.post('/projects/{project_id}/members/{user_id}', response_model=ProjectOut, tags=["projects"])
async def add_team_member(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    admin_check = db.query(ProjectUser).filter(
        ProjectUser.project_id == project_id,
        ProjectUser.user_id == current_user.id,
        ProjectUser.role == UserRole.admin.value
    ).first()
    
    if not admin_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project admin can add team members"
        )


    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    

    existing_member = db.query(ProjectUser).filter(
        ProjectUser.project_id == project_id,
        ProjectUser.user_id == user_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this project"
        )


    new_member = ProjectUser(
        project_id=project_id,
        user_id=user_id,
        role=UserRole.user.value
    )
    db.add(new_member)
    db.commit()
    
    return admin_check.project


@router.delete('/projects/{project_id}/members/{user_id}', response_model=ProjectOut, tags=["projects"])
async def remove_team_member(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
 
    admin_check = db.query(ProjectUser).filter(
        ProjectUser.project_id == project_id,
        ProjectUser.user_id == current_user.id,
        ProjectUser.role == UserRole.admin.value
    ).first()
    
    if not admin_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project admin can remove team members"
        )


    member = db.query(ProjectUser).filter(
        ProjectUser.project_id == project_id,
        ProjectUser.user_id == user_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this project"
        )


    if member.role == UserRole.admin.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the project admin"
        )

    db.delete(member)
    db.commit()
    
    return admin_check.project


@router.get('/projects/{project_id}/members', response_model=List[UserOut], tags=["projects"])
async def get_project_members(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    project_user = db.query(ProjectUser).filter(
        ProjectUser.project_id == project_id,
        ProjectUser.user_id == current_user.id
    ).first()
    
    if not project_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    members = db.query(User).join(ProjectUser).filter(
        ProjectUser.project_id == project_id
    ).all()
    
    return members