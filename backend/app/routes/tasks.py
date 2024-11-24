from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy.orm import Session
from db.database import get_db
from config.security import get_current_user
from db.models import User,Project,Task,TaskStatus,ProjectUser,UserRole
from schemas.task_schema import TaskCreate,TaskOut,TaskUpdate
from typing import List
from uuid import UUID
from routes.projects import get_project

#Comentarios
# No estaba definido en los requerimientos pero se considera que se debe manejar
# los delete como un soft delete, es decir, no se elimina el registro de la base de datos sino que se marca como eliminado cambiando el campo is_active a False

router = APIRouter()

@router.post('/projects/{project_id}/tasks',response_model=TaskOut,tags=["tasks"])
async def create_task(project_id:UUID,task:TaskCreate,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  project_user = db.query(ProjectUser).filter(ProjectUser.project_id == project_id, ProjectUser.user_id == current_user.id).first()
  if not project_user:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to access this project")

  db_task = Task(**task.model_dump(),project_id=project_id,status=TaskStatus.pending.value)
  db.add(db_task)
  db.commit()
  db.refresh(db_task)
  return db_task

@router.get('/projects/{project_id}/tasks', response_model=List[TaskOut], tags=['tasks'])
async def get_tasks(
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

    return db.query(Task).filter(Task.project_id == project_id).all()

@router.get('/projects/{project_id}/tasks/{task_id}', response_model=TaskOut, tags=['tasks'])
async def get_task_by_id(
    project_id: UUID,
    task_id: UUID,
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

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put('/projects/{project_id}/tasks/{task_id}', response_model=TaskOut, tags=["tasks"])
async def update_task(
    project_id: UUID,
    task_id: UUID,
    task_update: TaskUpdate,
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

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    update_data = task_update.model_dump(exclude_unset=True)

    if 'status' in update_data:
        if update_data['status'] not in [status.value for status in TaskStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )

    
    if 'assignee_id' in update_data:

        if update_data['assignee_id'] is not None:
            assignee_membership = db.query(ProjectUser).filter(
                ProjectUser.project_id == project_id,
                ProjectUser.user_id == update_data['assignee_id']
            ).first()
            
            if not assignee_membership:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee must be a project member"
                )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task

@router.delete('/projects/{project_id}/tasks/{task_id}', tags=['tasks'])
async def delete_task(
    project_id: UUID,
    task_id: UUID,
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
            detail="Only project admin can delete tasks"
        )

    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}