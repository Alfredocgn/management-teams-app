

def test_get_profile(client,test_user,auth_headers):
  response = client.get('/api/profile',headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert data["email"] == test_user.email
  assert data["first_name"] == test_user.first_name
  assert data["last_name"] == test_user.last_name

def test_get_profile_unauthorized(client):
  response = client.get('/api/profile')
  assert response.status_code == 401

def test_update_profile(client,auth_headers):
  update_data={
    "email":"update@example.com",
    "first_name":"updated",
    "last_name":"user",
    "password":"newPassword123"
  }
  response = client.put('/api/profile',json=update_data,headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert data["email"] == update_data["email"]
  assert data["first_name"] == update_data["first_name"]
  assert data["last_name"] == update_data["last_name"]

def test_update_profile_duplicate_email(client,auth_headers,db):
  from db.models import User
  from config.security import hash_password
  from uuid import uuid4

  other_user = User(
    id=uuid4(),
    email="other@example.com",
    first_name="firstName",
    last_name='lastName',
    hashed_password=hash_password('Password123'),
    is_subscribed = True
  )
  db.add(other_user)
  db.commit()

  update_data = {
    "email":"other@example.com",
    "first_name":"Update",
    "last_name":"User"
  }

  response = client.put("/api/profile",json=update_data,headers=auth_headers)
  assert response.status_code == 400
  assert "Email already exists" in response.json()["detail"]


def test_update_profile_invalid_email(client,auth_headers):
  update_data ={
    "email":"invalid-email",
    "first_name":"Updated",
    "last_name":"User"
  }

  response = client.put('/api/profile',json=update_data,headers=auth_headers)
  assert response.status_code == 422

def test_update_profile_empty_fields(client,auth_headers):
  update_data ={
  "email":"",
  "first_name":"",
  "last_name":""
}
  response = client.put('/api/profile',json=update_data,headers=auth_headers)
  assert response.status_code == 422

def test_update_profile_password_only(client,test_user,auth_headers,db):
  from db.models import User
  original_email = test_user.email
  original_first_name = test_user.first_name
  original_last_name = test_user.last_name

  update_data ={
    "password" :"NewPassword123"
  }
  response = client.put('/api/profile',json=update_data,headers=auth_headers)
  assert response.status_code == 200

  updated_user = db.query(User).filter(User.id == test_user.id).first()
  assert updated_user.email == original_email
  assert updated_user.first_name == original_first_name
  assert updated_user.last_name == original_last_name
