import pytest

from piper_driver.models import *
from piper_driver.repository import StagesRepository
from piper_driver.addins.exceptions import *


def test_repository_get(connection):
    user1 = User.create(email='1@email.com', role=UserRole.MASTER)
    user2 = User.create(email='2@email.com', role=UserRole.NORMAL)
    user3 = User.create(email='3@email.com', role=UserRole.NORMAL)
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, branch='master', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project1)
    stage = Stage.create(name='one', order=1, build=build)

    assert None is not StagesRepository.get(user1, stage.id)
    assert None is not StagesRepository.get(user3, stage.id)
    with pytest.raises(RepositoryPermissionDenied):
        assert None is not StagesRepository.get(user2, stage.id)


def test_repository_cancel(connection):
    user1 = User.create(email='1@email.com', role=UserRole.MASTER)
    user2 = User.create(email='2@email.com', role=UserRole.NORMAL)
    user3 = User.create(email='3@email.com', role=UserRole.NORMAL)
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project1)
    stage = Stage.create(name='one', order=1, build=build)

    StagesRepository.cancel(user1, stage.id)
    assert Stage.get(Stage.id == stage).status is StageStatus.CANCELED

    stage = Stage.create(name='one', order=2, build=build)
    with pytest.raises(RepositoryPermissionDenied):
        StagesRepository.cancel(user2, stage.id)
    assert Stage.get(Stage.id == stage).status is not StageStatus.CANCELED


