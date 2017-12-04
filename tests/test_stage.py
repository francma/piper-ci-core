import pytest

from piper_core.model import *
from piper_core.container import Container
from piper_core.utils.exceptions import *


def test_repository_get(container: Container):
    user1 = User.create(email='1@email.com', role=UserRole.MASTER, public_key='AAA')
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, branch='master', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='one', order=1, build=build)

    facade = container.get_stages_facade()
    assert None is not facade.get(user1, stage.id)


def test_repository_cancel(container: Container):
    user1 = User.create(email='1@email.com', role=UserRole.MASTER, public_key='ssh-rsa AAA')
    user2 = User.create(email='2@email.com', role=UserRole.NORMAL, public_key='ssh-rsa AAB')
    user3 = User.create(email='3@email.com', role=UserRole.NORMAL, public_key='ssh-rsa AAC')
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    ProjectUser.create(role=ProjectRole.DEVELOPER, user=user3, project=project1)
    stage1 = Stage.create(name='one', order=1, build=build)
    stage2 = Stage.create(name='two', order=2, build=build)
    stage3 = Stage.create(name='three', order=3, build=build)
    Job.create(stage=stage1, image='alpine/3.5')
    Job.create(stage=stage2, image='alpine/3.5')
    Job.create(stage=stage3, image='alpine/3.5')

    facade = container.get_stages_facade()

    facade.cancel(user1, stage1.id)
    assert Stage.get(Stage.id == stage1).status is Status.CANCELED

    facade.cancel(user3, stage2.id)
    assert Stage.get(Stage.id == stage2).status is Status.CANCELED

    with pytest.raises(FacadeUnauthorized):
        facade.cancel(user2, stage3.id)
    assert Stage.get(Stage.id == stage3).status is not Status.CANCELED
