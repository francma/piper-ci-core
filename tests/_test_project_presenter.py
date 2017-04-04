import json

from piper_driver.app import app
from piper_driver.models import *

app.testing = True


def test_projects_visibility(connection):
    """
    Project(A): user1
    Project(B): user1, user2
    Project(C): user2
    
    User(root): ROOT
    User(user1): USER
    User(user2): USER
    """
    project_a = Project.create(url='http://A', origin='http://A')
    project_b = Project.create(url='http://B', origin='http://A')
    project_c = Project.create(url='http://C', origin='http://A')

    user_root = User.create(email='email1', role=UserRole.ROOT)
    user_user1 = User.create(email='email2', role=UserRole.USER)
    user_user2 = User.create(email='email3', role=UserRole.USER)

    ProjectUser.create(user=user_user1, role=ProjectRole.DEVELOPER, project=project_a)
    ProjectUser.create(user=user_user1, role=ProjectRole.DEVELOPER, project=project_b)
    ProjectUser.create(user=user_user2, role=ProjectRole.DEVELOPER, project=project_b)
    ProjectUser.create(user=user_user2, role=ProjectRole.DEVELOPER, project=project_c)

    client = app.test_client()

    ###########################################
    r = client.get('/project', headers={'Authorization': 'Bearer ' + user_user1.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    expected = set([project_a.id, project_b.id])
    print(data)
    for row in data:
        entity = Project.get(Project.id == row['id'])
        assert entity.id == row['id']
        assert entity.url == row['url']
        assert ProjectUser.get(ProjectUser.project == entity).role.value == row['role']
        expected.remove(entity.id)
    assert len(expected) == 0

    r = client.get('/project/{}'.format(project_a.id), headers={'Authorization': 'Bearer ' + user_user1.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    assert project_a.id == data['id']
    assert project_a.url == data['url']
    assert ProjectUser.get(ProjectUser.project == project_a).role.value == data['role']

    r = client.get('/project/{}'.format(project_b.id), headers={'Authorization': 'Bearer ' + user_user1.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    assert project_b.id == data['id']
    assert project_b.url == data['url']
    assert ProjectUser.get(ProjectUser.project == project_b).role.value == data['role']

    r = client.get('/project/{}'.format(project_c.id), headers={'Authorization': 'Bearer ' + user_user1.token})
    data = json.loads(r.get_data())
    print(data)
    assert r.status_code == 404

    ###########################################

    r = client.get('/project', headers={'Authorization': 'Bearer ' + user_user2.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    expected = set([project_b.id, project_c.id])
    print(data)
    for row in data:
        print(row)
        entity = Project.get(Project.id == row['id'])
        assert entity.id == row['id']
        assert entity.url == row['url']
        assert ProjectUser.get(ProjectUser.project == entity).role.value == row['role']
        expected.remove(entity.id)
    assert len(expected) == 0

    r = client.get('/project/{}'.format(project_b.id), headers={'Authorization': 'Bearer ' + user_user2.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    assert project_b.id == data['id']
    assert project_b.url == data['url']
    assert ProjectUser.get(ProjectUser.project == project_b).role.value == data['role']

    r = client.get('/project/{}'.format(project_c.id), headers={'Authorization': 'Bearer ' + user_user2.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    assert project_c.id == data['id']
    assert project_c.url == data['url']
    assert ProjectUser.get(ProjectUser.project == project_c).role.value == data['role']

    r = client.get('/project/{}'.format(project_a.id), headers={'Authorization': 'Bearer ' + user_user2.token})
    data = json.loads(r.get_data())
    print(data)
    assert r.status_code == 404

    ###########################################

    r = client.get('/project', headers={'Authorization': 'Bearer ' + user_root.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    expected = set([project_a.id, project_b.id, project_c.id])
    print(data)
    for row in data:
        entity = Project.get(Project.id == row['id'])
        assert entity.id == row['id']
        assert entity.url == row['url']
        expected.remove(entity.id)
    assert len(expected) == 0

    r = client.get('/project/{}'.format(project_a.id), headers={'Authorization': 'Bearer ' + user_root.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    assert project_a.id == data['id']
    assert project_a.url == data['url']

    r = client.get('/project/{}'.format(project_b.id), headers={'Authorization': 'Bearer ' + user_root.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    assert project_b.id == data['id']
    assert project_b.url == data['url']

    r = client.get('/project/{}'.format(project_c.id), headers={'Authorization': 'Bearer ' + user_root.token})
    assert r.status_code == 200
    data = json.loads(r.get_data())
    assert project_c.id == data['id']
    assert project_c.url == data['url']



