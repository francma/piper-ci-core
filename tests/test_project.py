import json

import pytest

from piper_core.model import *
from piper_core.utils.exceptions import *
from piper_core.container import Container


def test_repository_get(container: Container):
    projects_facade = container.get_projects_facade()
    project1 = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    user1 = User.create(role=UserRole.NORMAL, email='1@email.com', public_key='AAA')
    assert None is not projects_facade.get(user1, project1.id)


def test_repository_list_count(container: Container):
    projects_facade = container.get_projects_facade()
    Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo1.git')
    Project.create(url='https://B', origin='https://github.com/francma/piper-ci-test-repo2.git')
    user1 = User.create(role=UserRole.NORMAL, email='1@email.com', public_key='AAA')

    assert len(projects_facade.list(user1, dict(), list(), 10, 0)) == 2

    assert projects_facade.count(user1, dict()) == 2


def test_repository_create(container: Container):
    projects_facade = container.get_projects_facade()
    user1 = User.create(role=UserRole.NORMAL, email='1@email.com', public_key='ssh-rsa AAB')
    user2 = User.create(role=UserRole.MASTER, email='2@email.com', public_key='ssh-rsa AAC')
    user3 = User.create(role=UserRole.ADMIN, email='3@email.com', public_key='ssh-rsa AAD')

    url = 'https://A'
    origin = 'https://github.com/francma/piper-ci-test-repo.git'
    with pytest.raises(FacadeUnauthorized):
        projects_facade.create(user1, {'url': url, 'origin': origin})
    assert Project.select().count() == 0

    projects_facade.create(user2, {'url': url, 'origin': origin})
    projects = list(Project.select())
    assert len(projects) == 1
    assert projects[0].url == url
    assert projects[0].origin == origin
    assert projects[0].delete().execute()

    projects_facade.create(user3, {'url': url, 'origin': origin})
    projects = list(Project.select())
    assert len(projects) == 1
    assert projects[0].url == url
    assert projects[0].origin == origin


def test_repository_update(container: Container):
    projects_facade = container.get_projects_facade()
    origin = 'https://github.com/francma/piper-ci-test-repo.git'
    project1 = Project.create(url='https://A', origin=origin, public_key='AAA')
    user1 = User.create(role=UserRole.NORMAL, email='1@email.com', public_key='ssh-rsa AAB')
    user2 = User.create(role=UserRole.MASTER, email='2@email.com', public_key='ssh-rsa AAC')
    user3 = User.create(role=UserRole.NORMAL, email='3@email.com', public_key='ssh-rsa AAD')
    ProjectUser.create(user=user3, project=project1, role=ProjectRole.MASTER)

    with pytest.raises(FacadeUnauthorized):
        projects_facade.update(user1, project1.id, {'url': 'https://B', 'origin': origin})

    projects_facade.update(user2, project1.id, {'url': 'https://B', 'origin': origin})
    project1 = Project.get(Project.id == project1.id)
    assert project1.url == 'https://B'
    assert project1.origin == origin

    projects_facade.update(user3, project1.id, {'url': 'https://C', 'origin': origin})
    project1 = Project.get(Project.id == project1.id)
    assert project1.url == 'https://C'
    assert project1.origin == origin


def test_rest_get(container: Container):
    app = container.get_app()
    app.testing = True
    project1 = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo1.git')
    user1 = User.create(role=UserRole.MASTER, email='2@email.com', public_key='AAA')

    client = app.test_client()
    r = client.get('/projects/' + str(project1.id), headers={'Authorization': 'Bearer ' + str(user1.token)})
    assert r.status_code == 200
    assert r.mimetype == 'application/json'
    assert json.loads(r.get_data(as_text=True))
