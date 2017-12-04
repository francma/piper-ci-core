import pytest
import yaml

from piper_core.model import *
from piper_core.container import Container
from piper_core.utils.exceptions import *


def test_repository_get(container: Container):
    builds_facade = container.get_builds_facade()

    user1 = User.create(email='1@email.com', role=UserRole.MASTER, public_key='ssh-rsa AAA')
    user3 = User.create(email='3@email.com', role=UserRole.GUEST, public_key='ssh-rsa AAB')
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, branch='master', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    assert None is not builds_facade.get(user1, build.id)
    assert None is not builds_facade.get(user3, build.id)


def test_repository_cancel(container: Container):
    user1 = User.create(email='1@email.com', role=UserRole.MASTER, public_key='ssh-rsa AAA')
    user2 = User.create(email='2@email.com', role=UserRole.NORMAL, public_key='ssh-rsa AAB')
    user3 = User.create(email='3@email.com', role=UserRole.NORMAL, public_key='ssh-rsa AAC')
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')

    builds_facade = container.get_builds_facade()

    build = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=0, build=build)
    job = Job.create(stage=stage, image='alpine/3.5')

    ProjectUser.create(role=ProjectRole.DEVELOPER, user=user3, project=project1)
    builds_facade.cancel(user1, build.id)
    assert Build.get(Build.id == build.id).status is Status.CANCELED
    assert Job.get(Job.id == job.id).status is Status.CANCELED
    assert Stage.get(Stage.id == stage.id).status is Status.CANCELED

    build = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=0, build=build)
    job = Job.create(stage=stage, image='alpine/3.5')

    with pytest.raises(FacadeUnauthorized):
        builds_facade.cancel(user2, build.id)
    assert Build.get(Build.id == build.id).status is not Status.CANCELED
    assert Job.get(Job.id == job.id).status is not Status.CANCELED
    assert Stage.get(Stage.id == stage.id).status is not Status.CANCELED


def test_repository_list_count(container: Container):
    builds_facade = container.get_builds_facade()

    user1 = User.create(email='a@martinfranc.eu', role=UserRole.MASTER, public_key='ssh-rsa AAA')
    user2 = User.create(email='c@martinfranc.eu', role=UserRole.GUEST, public_key='ssh-rsa AAC')
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    builds = builds_facade.list(user1)
    assert builds_facade.count(user1) == 3
    assert len(builds) == 3

    builds = builds_facade.list(user2)
    assert builds_facade.count(user2) == 3
    assert len(builds) == 3


def test_parse_config(container: Container):
    builds_facade = container.get_builds_facade()

    with open('tests/configs/basic.yml') as fd:
        contents = yaml.load(fd)

    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build1 = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    builds_facade.create_build(contents, build1)
    stage1 = Stage.get(Stage.name == 'one')
    job1: Job = Job.get(Job.stage == stage1)
    assert job1.only == "branch == master"
    assert job1.group == "RUNNER"
    assert job1.image == "IMAGE"
    assert job1.environment['a'] == 'a'
    assert job1.environment['b'] == 1
    assert len(job1.commands) == 2

    stage2 = Stage.get(Stage.name == 'two')
    Job.get(Job.stage == stage2)
