from fastapi import FastAPI,Depends
from db import models
from db.database import engine, SessionLocal,get_db
from sqlalchemy.orm import Session
from routes import auth,users,projects,tasks


app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router,prefix="/api")
app.include_router(projects.router,prefix="/api")
app.include_router(tasks.router,prefix="/api")

def get_db_session(db:Session = Depends(get_db)):
  return db

@app.on_event("startup")
async def startup():
  models.Base.metadata.create_all(bind=engine)

