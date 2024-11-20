from passlib.context import CryptContext
from dotenv import load_dotenv
from jose import JWTError,jwt
import os
from typing import Optional
from datetime import timedelta,datetime,timezone
from fastapi import HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User

load_dotenv()

ACCESS_TOKEN_EXPIRES_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto",bcrypt__rounds=12)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password:str) -> str :
  return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str) -> bool :
  return pwd_context.verify(plain_password,hashed_password)


def create_access_token(data:dict,expires_delta: Optional[timedelta] = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(timezone.utc) +  expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
  to_encode.update({"exp":expire})
  encoded_jwt = jwt.encode(to_encode,JWT_SECRET_KEY,algorithm=JWT_ALGORITHM)
  return encoded_jwt

def verify_token(token:str) -> dict :
  try:
    payload = jwt.decode(token,JWT_SECRET_KEY,algorithms=[JWT_ALGORITHM])
    return payload
  except JWTError:
    raise HTTPException(
      status_code= status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate":"Bearer"}
    )

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)  
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = verify_token(token)
    email: str = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user