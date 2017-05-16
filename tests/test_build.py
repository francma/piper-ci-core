import pytest

from piper_driver.models import *
from piper_driver.repository import BuildRepository


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
    user1 = User.create(email='a@martinfranc.eu', role=UserRole.MASTER)
    user2 = User.create(email='b@martinfranc.eu', role=UserRole.NORMAL)
    user3 = User.create(email='c@martinfranc.eu', role=UserRole.NORMAL)
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project1)

    expected = {
        'id': build.id,
        'project_id': project1.id,
        'status': BuildStatus.CREATED,
    }
    actual = BuildRepository.get(build.id, user1)
    assert expected == actual

    actual = BuildRepository.get(build.id, user3)
    assert expected == actual

    with pytest.raises(RepositoryPermissionDenied):
        BuildRepository.get(build.id, user2)


def test_repository_delete(connection):
    user1 = User.create(email='a@martinfranc.eu', role=UserRole.MASTER)
    user2 = User.create(email='b@martinfranc.eu', role=UserRole.NORMAL)
    user3 = User.create(email='c@martinfranc.eu', role=UserRole.NORMAL)
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')

    build = Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project1)
    BuildRepository.delete(build.id, user1)
    assert Build.get(Build.id == build.id).status is BuildStatus.CANCELED

    build = Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    with pytest.raises(RepositoryPermissionDenied):
        BuildRepository.delete(build.id, user2)
    assert Build.get(Build.id == build.id).status is not BuildStatus.CANCELED


def test_repository_list(connection):
    user1 = User.create(email='a@martinfranc.eu', role=UserRole.MASTER)
    user2 = User.create(email='b@martinfranc.eu', role=UserRole.NORMAL)
    user3 = User.create(email='c@martinfranc.eu', role=UserRole.NORMAL)

    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    project2 = Project.create(url='https://2', origin='https://github.com/francma/piper-ci-test2-repo.git')
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project1)
    ProjectUser.create(role=ProjectRole.GUEST, user=user2, project=project2)

    Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    Build.create(project=project2, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    Build.create(project=project2, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')

    builds = BuildRepository.list({}, [], 10, 0, user3)
    assert len(builds) == 3

    builds = BuildRepository.list({}, [], 10, 0, user2)
    assert len(builds) == 2

    ProjectUser.create(role=ProjectRole.GUEST, user=user2, project=project1)
    ProjectUser.create(role=ProjectRole.GUEST, user=user3, project=project2)

    builds = BuildRepository.list({}, [], 10, 0, user3)
    assert len(builds) == 5

    builds = BuildRepository.list({}, [], 10, 0, user2)
    assert len(builds) == 5

    builds = BuildRepository.list({'project_id': project1.id}, [], 10, 0, user3)
    assert len(builds) == 3

    builds = BuildRepository.list({'project_id': project2.id, 'status': BuildStatus.CREATED.to_str()}, [], 10, 0, user3)
    assert len(builds) == 2

    builds = BuildRepository.list({}, ['created-asc'], 10, 0, user3)
    assert len(builds) == 5
    assert builds[0]['id'] < builds[1]['id'] < builds[2]['id'] < builds[3]['id'] < builds[4]['id']

    builds = BuildRepository.list({}, ['created-desc'], 10, 0, user3)
    assert len(builds) == 5
    assert builds[0]['id'] > builds[1]['id'] > builds[2]['id'] > builds[3]['id'] > builds[4]['id']

    builds = BuildRepository.list({'user_id': user1.id}, [], 10, 0, user1)
    assert len(builds) == 0

    builds = BuildRepository.list({}, [], 10, 0, user1)
    print(builds)
    assert len(builds) == 5
