

def test_create_project(client,test_user,auth_headers):
  project_data = {
    "title":"Test Project",
    "description":"Test Description"
  }
  response = client.post('/api/projects',json=project_data,headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert data['title'] == project_data["title"]
  assert data["description"] == project_data["description"]
  assert data["owner_id"] == str(test_user.id)

def test_create_project_unauthorized(client):
  project_data={
    "title":"Test Project",
    "description":"Test Description"
  }
  response = client.post('/api/projects',json=project_data)
  assert response.status_code == 401

def test_create_project_unsubscribed(client,test_user,db):

  test_user.is_subscribed = False
  db.commit()
  response = client.post("/login", data={
    "username": test_user.email,
    "password": "Password123",
    "grant_type": "password"
  })
  token = response.json()["access_token"]
  headers = {"Authorization": f"Bearer {token}"}
  project_data={
    "title":"Test Project",
    "description":"Test Description"
  }
  response = client.post('/api/projects',json=project_data,headers=headers)
  assert response.status_code == 403
  assert "User is not subscribed" in response.json()['detail']

def test_get_projects(client,test_user,auth_headers,db):
  from db.models import Project
  from uuid import uuid4

  project = Project(
    id=uuid4(),
    title="Test Project",
    description = "Test Description",
    owner_id = test_user.id
  )
  db.add(project)
  db.commit()

  response = client.get('/api/projects',headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert len(data) == 1
  assert data[0]['title'] == 'Test Project'
  assert data[0]['owner_id'] == str(test_user.id)

def test_get_project_by_id(client,test_user,auth_headers,db):
  from db.models import Project
  from uuid import uuid4

  project = Project(
  id=uuid4(),
  title="Test Project",
  description = "Test Description",
  owner_id = test_user.id
  )
  db.add(project)
  db.commit()

  response = client.get(f'/api/projects/{project.id}',headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert data['title'] == project.title
  assert data['owner_id'] == str(test_user.id)

def test_get_project_not_found(client,auth_headers):
  from uuid import uuid4
  fake_id = uuid4()
  response = client.get(f'/api/projects/{fake_id}',headers=auth_headers)
  assert response.status_code == 404

def test_update_project(client,test_user,auth_headers,db):
  from db.models import Project
  from uuid import uuid4

  project = Project(
    id=uuid4(),
    title="Original Title",
    description="Original Description",
    owner_id=test_user.id
  )
  db.add(project)
  db.commit()

  update_data = {
    "title":"Updated Title",
    "description":"Updated Description"
  }
  response = client.put(f'/api/projects/{project.id}',json=update_data,headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert data['title'] == update_data['title']
  assert data['description'] == update_data['description']


