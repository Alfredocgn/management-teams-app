from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from db.models import User
from config.security import get_current_user
from db.database import get_db
from config.security import hash_password
from schemas.user_schema import UserOut,UserUpdate



router = APIRouter()


@router.get('/profile',response_model=UserOut,tags=['users'])
async def get_profile(user:User= Depends(get_current_user)):
  return user


@router.put('/profile',response_model=UserOut,tags=['users'])
async def update_user(
  user_update:UserUpdate,
  current_user:User=Depends(get_current_user),
  db:Session=Depends(get_db)
):
  if user_update.email:
    existing_user = db.query(User).filter(User.email == user_update.email).first()
    if existing_user and existing_user.id != current_user.id:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already exists")
    
    current_user.email = user_update.email
    current_user.first_name = user_update.first_name
    current_user.last_name = user_update.last_name
  if user_update.password:
    current_user.hashed_password = hash_password(user_update.password)
  db.commit()
  db.refresh(current_user)
  return current_user

@router.get("/users",response_model=list[UserOut],tags=['users'])
async def get_users(skip:int=0,limit:int=10,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
  # if not current_user.is_subscribed:
  #   raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User is not subscribed")
  
  return db.query(User).offset(skip).limit(limit).all()


@router.delete('/profile',tags=["users"])
async def delete_user(
  current_user:User=Depends(get_current_user),
  db:Session=Depends(get_db)

):
  try:
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}
  except Exception as e:
    raise HTTPException(
      status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail = "Error deleting user"
    )