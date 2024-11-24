from fastapi import FastAPI,Depends
from db import models
from db.database import engine,get_db
from sqlalchemy.orm import Session
from routes import auth,users,projects,tasks,stripe_subscription
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://hkdk.events",
        "https://events.hookdeck.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "stripe-signature"],  
)
app.include_router(auth.router)
app.include_router(users.router,prefix="/api")
app.include_router(projects.router,prefix="/api")
app.include_router(tasks.router,prefix="/api")
app.include_router(stripe_subscription.router,prefix="/api")

def get_db_session(db:Session = Depends(get_db)):
  return db

@app.on_event("startup")
async def startup():
  models.Base.metadata.create_all(bind=engine)

