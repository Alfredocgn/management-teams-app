

def test_create_project(client, test_user, auth_headers, db):
    from db.models import Project,ProjectUser,UserRole
    from uuid import UUID
    project_data = {
        "title": "Test Project",
        "description": "Test Description"
    }
    response = client.post('/api/projects', json=project_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == project_data["title"]
    assert data["description"] == project_data["description"]
    
    project = db.query(Project).filter(Project.title == project_data["title"]).first()
    assert project is not None

    project_user = db.query(ProjectUser).filter(
        ProjectUser.project_id == UUID(data["id"]),
        ProjectUser.user_id == test_user.id
    ).first()
    
    assert project_user is not None
    assert project_user.role == UserRole.admin.value

def test_create_project_unauthorized(client):
  project_data={
    "title":"Test Project",
    "description":"Test Description"
  }
  response = client.post('/api/projects',json=project_data)
  assert response.status_code == 401

def test_create_project_unsubscribed(client, test_user, auth_headers, db):
    from db.models import StripeSubscription
    db.query(StripeSubscription).filter(StripeSubscription.user_id == test_user.id).delete()
    db.commit()

    project_data = {
        "title": "Test Project",
        "description": "Test Description"
    }
    response = client.post('/api/projects', json=project_data, headers=auth_headers)
    assert response.status_code == 403
    assert "User is not subscribed" in response.json()['detail']

def test_get_projects(client,test_user,auth_headers,db):
  from db.models import Project,ProjectUser,UserRole
  from uuid import uuid4

  project = Project(
    id=uuid4(),
    title="Test Project",
    description = "Test Description",
  )
  db.add(project)
  db.commit()

  project_user = ProjectUser(
    project_id=project.id,
    user_id=test_user.id,
    role=UserRole.admin.value
  )
  db.add(project_user)
  db.commit()

  response = client.get('/api/projects',headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert len(data) == 1
  assert data[0]['title'] == 'Test Project'

def test_get_project_by_id(client,test_user,auth_headers,db):
  from db.models import Project,ProjectUser,UserRole
  from uuid import uuid4

  project = Project(
  id=uuid4(),
  title="Test Project",
  description = "Test Description",
  )
  db.add(project)
  db.commit()

  project_user = ProjectUser(
    project_id=project.id,
    user_id=test_user.id,
    role=UserRole.admin.value
  )
  db.add(project_user)
  db.commit()

  response = client.get(f'/api/projects/{project.id}',headers=auth_headers)
  assert response.status_code == 200
  data = response.json()
  assert data['title'] == project.title


def test_get_project_not_found(client,auth_headers):
  from db.models import Project,ProjectUser,UserRole
  from uuid import uuid4
  fake_id = uuid4()
  response = client.get(f'/api/projects/{fake_id}',headers=auth_headers)
  assert response.status_code == 404

def test_update_project(client,test_user,auth_headers,db):
  from db.models import Project,ProjectUser,UserRole
  from uuid import uuid4

  project = Project(
    id=uuid4(),
    title="Original Title",
    description="Original Description",

  )
  db.add(project)
  db.commit()

  project_user = ProjectUser(
    project_id=project.id,
    user_id=test_user.id,
    role=UserRole.admin.value
  )
  db.add(project_user)
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


def test_update_project_not_admin(client, test_user, auth_headers, db):
    from db.models import Project,ProjectUser,UserRole
    from uuid import uuid4

    project = Project(
        id=uuid4(),
        title="Original Title",
        description="Original Description"
    )
    db.add(project)
    db.commit()

    project_user = ProjectUser(
        project_id=project.id,
        user_id=test_user.id,
        role=UserRole.user.value 
    )
    db.add(project_user)
    db.commit()

    update_data = {
        "title": "Updated Title",
        "description": "Updated Description"
    }
    response = client.put(f'/api/projects/{project.id}', json=update_data, headers=auth_headers)
    assert response.status_code == 403
    assert "Only project admin can update the project" in response.json()['detail']

def test_add_team_member(client, test_user, auth_headers, db):
    from db.models import Project, ProjectUser, UserRole, User, StripeSubscription
    from uuid import uuid4
    from datetime import datetime

    project = Project(
        id=uuid4(),
        title="Test Project",
        description="Test Description"
    )
    db.add(project)
    db.commit()

    project_user = ProjectUser(
        project_id=project.id,
        user_id=test_user.id,
        role=UserRole.admin.value
    )
    db.add(project_user)
    db.commit()

    new_user_id = uuid4()
    new_user = User(
        id=new_user_id,
        email="newuser@test.com",
        first_name="New",
        last_name="User",
        password="String123"
    )
    db.add(new_user)
    db.commit()

    subscription = StripeSubscription(
        id=uuid4(),
        user_id=new_user_id,
        subscription_id="sub_test123",
        status="active",
        current_period_start=datetime.utcnow()
    )
    db.add(subscription)
    db.commit()

    response = client.post(
        f'/api/projects/{project.id}/members/{new_user_id}',
        headers=auth_headers
    )
    assert response.status_code == 200


    member = db.query(ProjectUser).filter(
        ProjectUser.project_id == project.id,
        ProjectUser.user_id == new_user_id
    ).first()
    assert member is not None
    assert member.role == UserRole.user.value

def test_remove_team_member(client, test_user, auth_headers, db):
    from db.models import Project, ProjectUser, UserRole, User, StripeSubscription
    from uuid import uuid4
    from datetime import datetime
    
    project = Project(
        id=uuid4(),
        title="Test Project",
        description="Test Description"
    )
    db.add(project)
    db.commit()

    admin_user = ProjectUser(
        project_id=project.id,
        user_id=test_user.id,
        role=UserRole.admin.value
    )
    db.add(admin_user)
    db.commit()

    member_user_id = uuid4()
    member_user = User(
        id=member_user_id,
        email="member@test.com",
        first_name="Member",
        last_name="User",
        password="String123"
    )
    db.add(member_user)
    db.commit()

    subscription = StripeSubscription(
        id=uuid4(),
        user_id=member_user_id,
        subscription_id="sub_test123",
        status="active",
        current_period_start=datetime.utcnow()
    )
    db.add(subscription)
    db.commit()

    member_project_user = ProjectUser(
        project_id=project.id,
        user_id=member_user_id,
        role=UserRole.user.value
    )
    db.add(member_project_user)
    db.commit()

    response = client.delete(
        f'/api/projects/{project.id}/members/{member_user_id}',
        headers=auth_headers
    )
    assert response.status_code == 200

    member = db.query(ProjectUser).filter(
        ProjectUser.project_id == project.id,
        ProjectUser.user_id == member_user_id
    ).first()
    assert member is None