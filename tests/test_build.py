import pytest

from piper_driver.models import *
from piper_driver.repository import BuildsRepository
from piper_driver.addins.exceptions import *


def test_model(connection):
    pass
    # project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    # build = Build()
    # build.project = project1
    # with pytest.raises(ModelInvalid):
    #     build.ref = 'master'
    #     build.commit = 'invalid'
    #     build.save()
    # with pytest.raises(ModelInvalid):
    #     build.ref = 'master'
    #     build.commit = list()
    #     build.save()
    # with pytest.raises(ModelInvalid):
    #     build.commit = '634721d9da222050d41dce164d9de35fe475aa7a'
    #     build.ref = 1
    #     build.save()
    # with pytest.raises(ModelInvalid):
    #     build.commit = '634721d9da222050d41dce164d9de35fe475aa7a'
    #     build.ref = list()
    #     build.save()
    # build.commit = '634721d9da222050d41dce164d9de35fe475aa7a'
    # build.ref = 'master'


def test_repository_get(connection):
    user1 = User.create(email='1@email.com', role=UserRole.MASTER)
    user2 = User.create(email='2@email.com', role=UserRole.NORMAL)
    user3 = User.create(email='3@email.com', role=UserRole.NORMAL)
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, branch='master', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project1)

    assert None is not BuildsRepository.get(user1, build.id)
    assert None is not BuildsRepository.get(user3, build.id)
    with pytest.raises(RepositoryPermissionDenied):
        BuildsRepository.get(user2, build.id)


def test_repository_cancel(connection):
    user1 = User.create(email='1@email.com', role=UserRole.MASTER)
    user2 = User.create(email='2@email.com', role=UserRole.NORMAL)
    user3 = User.create(email='3@email.com', role=UserRole.NORMAL)
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')

    build = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project1)
    BuildsRepository.cancel(user1, build.id)
    assert Build.get(Build.id == build.id).status is BuildStatus.CANCELED

    build = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    with pytest.raises(RepositoryPermissionDenied):
        BuildsRepository.cancel(user2, build.id)
    assert Build.get(Build.id == build.id).status is not BuildStatus.CANCELED


def test_repository_list_count(connection):
    user1 = User.create(email='a@martinfranc.eu', role=UserRole.MASTER)
    user2 = User.create(email='b@martinfranc.eu', role=UserRole.NORMAL)
    user3 = User.create(email='c@martinfranc.eu', role=UserRole.NORMAL)

    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    project2 = Project.create(url='https://2', origin='https://github.com/francma/piper-ci-test2-repo.git')
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project1)
    ProjectUser.create(role=ProjectRole.GUEST, user=user2, project=project2)

    Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    Build.create(project=project2, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    Build.create(project=project2, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    builds = BuildsRepository.list(user3)
    assert len(builds) == 3

    builds = BuildsRepository.list(user2)
    assert len(builds) == 2

    ProjectUser.create(role=ProjectRole.GUEST, user=user2, project=project1)
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project2)

    builds = BuildsRepository.list(user3)
    assert len(builds) == 5
    assert BuildsRepository.count(user3) == 5

    builds = BuildsRepository.list(user2, {}, [], 10, 0)
    assert BuildsRepository.count(user2) == 5
    assert len(builds) == 5

    builds = BuildsRepository.list(user3, {'project_id': project1.id})
    assert BuildsRepository.count(user3, {'project_id': project1.id}) == 3
    assert len(builds) == 3

    builds = BuildsRepository.list(user3, {'project_id': project2.id, 'status': BuildStatus.CREATED.to_str()})
    assert BuildsRepository.count(user3, {'project_id': project2.id, 'status': BuildStatus.CREATED.to_str()}) == 2
    assert len(builds) == 2

    builds = BuildsRepository.list(user3, order=['created-asc'])
    assert len(builds) == 5
    assert builds[0]['id'] < builds[1]['id'] < builds[2]['id'] < builds[3]['id'] < builds[4]['id']

    builds = BuildsRepository.list(user3, order=['created-desc'])
    assert len(builds) == 5
    assert builds[0]['id'] > builds[1]['id'] > builds[2]['id'] > builds[3]['id'] > builds[4]['id']

    builds = BuildsRepository.list(user1, {'user_id': user1.id})
    assert len(builds) == 0

    builds = BuildsRepository.list(user1)
    assert len(builds) == 5
