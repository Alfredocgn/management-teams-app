from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy.orm import Session
from db.database import get_db
from config.security import get_current_user
from db.models import User,Project,Task,TaskStatus
from schemas.task_schema import TaskCreate,TaskOut,TaskUpdate
from typing import List
from uuid import UUID
from routes.projects import get_project



router = APIRouter()

@router.post('/projects/{project_id}/tasks',response_model=TaskOut,tags=["tasks"])
async def create_task(project_id:UUID,task:TaskCreate,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  project = await get_project(project_id,current_user,db)

  if task.assignee_id:
    assignee = db.query(User).filter(User.id == task.assignee_id).first()
    if not assignee:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User to assigne task not found")
    if assignee.id not in [m.id for m in project.team_members] and assignee.id != project.owner_id:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Assignee must be a project member')
  
  db_task = Task(**task.model_dump(),project_id=project_id,status=TaskStatus.pending.value)
  db.add(db_task)
  db.commit()
  db.refresh(db_task)
  return db_task

@router.get('/projects/{project_id}/tasks',response_model=List[TaskOut],tags=['tasks'])
async def get_tasks(project_id:UUID,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  project = await get_project(project_id,current_user,db)

  return db.query(Task).filter(Task.project_id == project_id).all()

@router.get('/projects/{project_id}/tasks/{task_id}',response_model=TaskOut,tags=['tasks'])
async def get_task_by_id(
  project_id:UUID,
  task_id:UUID,
  current_user:User=Depends(get_current_user),
  db:Session=Depends(get_db)
):
  project = await get_project(project_id,current_user,db)
  task = db.query(Task).filter(Task.id == task_id,Task.project_id == project_id).first()
  if not task:
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail="Task not found")
  return task

@router.put('/projects/{project_id}/tasks/{task_id}', response_model=TaskOut, tags=["tasks"])
async def update_task(
    project_id: UUID,
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = await get_task_by_id(project_id,task_id, current_user, db)
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    if 'status' in update_data:
        if update_data['status'] not in [status.value for status in TaskStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status"
            )
    
    if 'assignee_id' in update_data:
        assignee = db.query(User).filter(User.id == update_data['assignee_id']).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )
        if assignee.id not in [m.id for m in task.project.team_members] and assignee.id != task.project.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a project member"
            )
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete('/projects/{project_id}/tasks/{task_id}',tags=['tasks'])
async def delete_task(project_id:UUID,task_id:UUID,current_user:User=Depends(get_current_user),db:Session = Depends(get_db)):
  task = await get_task_by_id(project_id,task_id, current_user, db)

  db.delete(task)
  db.commit()
  return{"message":"Task deleted succesfully"}