import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from main import app
from db.models import User
from config.security import hash_password
from uuid import uuid4
from dotenv import load_dotenv
import os

load_dotenv()

TEST_DB = os.getenv('SQLALCHEMY_TEST_DATABASE_URL')

engine = create_engine(TEST_DB)
TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

@pytest.fixture(scope='function')
def db():
  Base.metadata.create_all(bind=engine)
  db = TestingSessionLocal()
  try:
    yield db
  finally:
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def client(db):
  def override_get_db():
    try:
      yield db
    finally:
      db.close()
  app.dependency_overrides[get_db] = override_get_db
  yield TestClient(app)
  app.dependency_overrides.clear()

@pytest.fixture(scope='function')
def test_user(db):
  user = User(
    id = uuid4(),
    email="test@example.com",
    first_name="Test",
    last_name = "User",
    hashed_password=hash_password("Password123"),
    is_subscribed=True,
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  return user

@pytest.fixture(scope="function")
def auth_headers(client,test_user):
  response = client.post("/login",data={
    "username":test_user.email,
    "password":"Password123"
  })
  token = response.json()["access_token"]
  return {"Authorization":f"Bearer {token}"}