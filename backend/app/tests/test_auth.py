

def test_register_user(client):
  response = client.post("/register",json={
    "email":"new@test.com",
    "password":"Password123",
    "first_name":"test",
    "last_name":"tester"

  })
  assert response.status_code == 200
  data = response.json()
  assert data["email"] == "new@test.com"
  assert "id" in data


def test_login_user(client,test_user):
  response = client.post('/login',data={
    "username":test_user.email,
    "password":"Password123",
    "grant_type":"password"
  })
  assert response.status_code == 200
  data = response.json()
  assert "access_token" in data
  assert "refresh_token" in data
  assert data["user"]["email"] == test_user.email

def test_login_invalid_credentials(client):
  response = client.post('/login',data={
    "username": "wrong@email.com",
    "password": "wrongpass",
    "grant_type":"password"
  })
  assert response.status_code == 401 

def test_register_invalid_password_no_number(client):
  response = client.post('/register',json={
    "email": "test@example.com",
    "password": "Password", 
    "first_name": "test",
    "last_name": "user"

  })
  assert response.status_code == 422
  assert  "Password must contain at least one number" in response.json()["detail"][0]["msg"]

def test_register_invalid_password_no_uppercase(client):
    response = client.post("/register", json={
        "email": "test@example.com",
        "password": "password123",  
        "first_name": "test",
        "last_name": "user"
    })
    assert response.status_code == 422
    assert "Password must contain at least one uppercase letter" in response.json()["detail"][0]["msg"]

def test_register_invalid_email(client):
    response = client.post("/register", json={
        "email": "invalid-email",
        "password": "Password123",
        "first_name": "test",
        "last_name": "user"
    })
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()["detail"][0]["msg"]

def test_register_empty_fields(client):
    response = client.post("/register", json={
        "email": "",
        "password": "",
        "first_name": "",
        "last_name": ""
    })
    assert response.status_code == 422

def test_login_empty_fields(client):
    response = client.post("/login", data={
        "username": "",
        "password": "",
        "grant_type": "password"
    })
    assert response.status_code == 422
    assert "Username and password cannot be empty" in response.json()["detail"]

