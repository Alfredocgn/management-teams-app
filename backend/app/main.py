from fastapi import FastAPI,Depends
import models
from database import engine, SessionLocal,get_db
from sqlalchemy.orm import Session


app = FastAPI()


def get_db_session(db:Session = Depends(get_db)):
  return db

@app.on_event("startup")
async def startup():
  models.Base.metadata.create_all(bind=engine)