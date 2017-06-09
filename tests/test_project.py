import json

import pytest

from piper_driver.app import app
from piper_driver.models import *
from piper_driver.addins.exceptions import *
from piper_driver.repository import ProjectRepository

app.testing = True


def test_model(connection):
    pass


def test_repository_get(connection):
    project1 = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    user1 = User.create(role=UserRole.NORMAL, email='1@email.com')
    user2 = User.create(role=UserRole.MASTER, email='2@email.com')
    user3 = User.create(role=UserRole.NORMAL, email='3@email.com')
    ProjectUser.create(user=user3, project=project1, role=ProjectRole.DEVELOPER)

    with pytest.raises(RepositoryPermissionDenied):
        ProjectRepository.get(user1, project1.id)

    assert None is not ProjectRepository.get(user2, project1.id)
    assert None is not ProjectRepository.get(user3, project1.id)


def test_repository_list_count(connection):
    project1 = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo1.git')
    project2 = Project.create(url='https://B', origin='https://github.com/francma/piper-ci-test-repo2.git')
    user1 = User.create(role=UserRole.NORMAL, email='1@email.com')
    user2 = User.create(role=UserRole.MASTER, email='2@email.com')
    user3 = User.create(role=UserRole.NORMAL, email='3@email.com')
    ProjectUser.create(user=user3, project=project1, role=ProjectRole.DEVELOPER)

    assert len(ProjectRepository.list(user1, dict(), list(), 10, 0)) == 0
    assert len(ProjectRepository.list(user2, dict(), list(), 10, 0)) == 2
    assert len(ProjectRepository.list(user3, dict(), list(), 10, 0)) == 1

    assert ProjectRepository.count(user1, dict()) == 0
    assert ProjectRepository.count(user2, dict()) == 2
    assert ProjectRepository.count(user3, dict()) == 1


def test_repository_create(connection):
    user1 = User.create(role=UserRole.NORMAL, email='1@email.com')
    user2 = User.create(role=UserRole.ADMIN, email='2@email.com')
    user3 = User.create(role=UserRole.MASTER, email='3@email.com')

    url = 'https://A'
    origin = 'https://github.com/francma/piper-ci-test-repo1.git'
    with pytest.raises(RepositoryPermissionDenied):
        ProjectRepository.create(user1, {'url': url, 'origin': origin})
    assert Project.select().count() == 0

    ProjectRepository.create(user2, {'url': url, 'origin': origin})
    projects = list(Project.select())
    assert len(projects) == 1
    projects[0].url == url
    projects[0].origin == origin
    projects[0].delete().execute()

    ProjectRepository.create(user3, {'url': url, 'origin': origin})
    projects = list(Project.select())
    assert len(projects) == 1
    projects[0].url == url
    projects[0].origin == origin


def test_repository_update(connection):
    origin = 'https://github.com/francma/piper-ci-test-repo.git'
    project1 = Project.create(url='https://A', origin=origin)
    user1 = User.create(role=UserRole.NORMAL, email='1@email.com')
    user2 = User.create(role=UserRole.MASTER, email='2@email.com')
    user3 = User.create(role=UserRole.NORMAL, email='3@email.com')
    ProjectUser.create(user=user3, project=project1, role=ProjectRole.DEVELOPER)

    with pytest.raises(RepositoryPermissionDenied):
        ProjectRepository.update(user1, project1.id, {'url': 'https://B', 'origin': origin})

    ProjectRepository.update(user2, project1.id, {'url': 'https://B', 'origin': origin})
    project1 = Project.get(Project.id == project1.id)
    assert project1.url == 'https://B'
    assert project1.origin == origin

    ProjectRepository.update(user3, project1.id, {'url': 'https://C', 'origin': origin})
    project1 = Project.get(Project.id == project1.id)
    assert project1.url == 'https://C'
    assert project1.origin == origin


def test_rest_get(connection):
    project1 = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo1.git')
    user1 = User.create(role=UserRole.MASTER, email='2@email.com')

    client = app.test_client()
    r = client.get('/projects/' + str(project1.id), headers={'Authorization': 'Bearer ' + str(user1.token)})
    assert r.status_code == 200
    assert json.loads(r.get_data())
