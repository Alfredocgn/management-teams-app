from fastapi import APIRouter,Depends,HTTPException,status
from schemas.user_schema import UserOut,UserCreate
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User
from config.security import hash_password,verify_password,create_access_token,verify_token,create_refresh_token,oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError




router = APIRouter()


@router.post('/register',response_model=UserOut,tags=['authentication'])
def register_user(user:UserCreate, db:Session= Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already exists")
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email,hashed_password=hashed_password,first_name=user.first_name,last_name=user.last_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post('/login',tags=['authentication'])
def login_user(form_data:OAuth2PasswordRequestForm = Depends(),db:Session=Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    access_token = create_access_token(data={"sub":user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_subscribed": user.is_subscribed
        }
    }

@router.post('/refresh', tags=['authentication'])
async def refresh_token_endpoint(
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = verify_token(current_token)
        if payload.get('type') != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type - must use refresh token"
            )
        
        email = payload.get('sub')
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        access_token = create_access_token(data={"sub": email})
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )