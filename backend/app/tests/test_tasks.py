

def test_create_task(client,test_user,auth_headers,db):
  from db.models import Project
  from uuid import uuid4
  from datetime import datetime,timedelta

  project = Project(
    id=uuid4(),
    title="Test Project",
    description="Test Description",
    owner_id = test_user.id
  )
  db.add(project)
  db.commit()
  project_id = str(project.id)

  task_data ={
    "title" :"Test Task",
    "description": "Test Description",
    "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
    

  }

  response = client.post(f'/api/projects/{project_id}/tasks',json=task_data,headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert data['title'] == task_data['title']
  assert data['description'] == task_data['description']
  assert data['project_id'] == project_id

def test_create_task_unauhtorized(client):
  from uuid import uuid4
  project_id = str(uuid4())

  response = client.post(f'/api/projects/{project_id}/tasks')
  assert response.status_code == 401

def test_get_tasks(client,test_user,auth_headers,db):
  from db.models import Project, Task
  from uuid import uuid4
  from datetime import datetime,timedelta

  project = Project(
    id=uuid4(),
    title="Test Project",
    description="Test Description",
    owner_id = test_user.id
  )
  db.add(project)
  db.commit()

  task = Task(
    id=uuid4(),
    title="Test Task",
    description = "Test Description",
    project_id=project.id,
    due_date=datetime.utcnow() + timedelta(days=1)
  )
  db.add(task)
  db.commit()

  response = client.get(f'/api/projects/{project.id}/tasks',headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert len(data) == 1
  assert data[0]['title'] == task.title

def test_update_task(client,test_user,auth_headers,db):
  from db.models import Project, Task
  from uuid import uuid4
  from datetime import datetime,timedelta

  project = Project(
    id=uuid4(),
    title="Test Project",
    description="Test Description",
    owner_id = test_user.id
  )
  db.add(project)
  db.commit()

  task = Task(
    id=uuid4(),
    title="Test Task",
    description = "Test Description",
    project_id=project.id,
    due_date=datetime.utcnow() + timedelta(days=1)
  )
  db.add(task)
  db.commit()

  update_data = {
    "title":"Updated Title",
    "description":"Updated Description",
    "status":"completed",
     "due_date": (datetime.utcnow() + timedelta(days=2)).isoformat()
  }
  response = client.put(f'/api/projects/{project.id}/tasks/{task.id}',json=update_data,headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert data['title'] == update_data['title']
  assert data['description'] == update_data['description']
  assert data['status'] == update_data['status']

def test_delete_task(client,test_user,auth_headers,db):
  from db.models import Project,Task
  from uuid import uuid4
  project = Project(
      id=uuid4(),
      title="Test Project",
      description="Test Description",
      owner_id=test_user.id
  )
  db.add(project)
  db.commit()

  task = Task(
      id=uuid4(),
      title="Test Task",
      description="Test Description",
      project_id=project.id
  )
  db.add(task)
  db.commit()

  response = client.delete(f'/api/projects/{project.id}/tasks/{task.id}',headers=auth_headers)
  assert response.status_code == 200
  task_exists = db.query(Task).filter(Task.id == task.id).first()
  assert task_exists is None 


