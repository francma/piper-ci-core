from piper_driver.models import *


def test_1(connection):
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='a', order=1, build=build)

    assert stage.status is StageStatus.CREATED
    Job.create(stage=stage, status=JobStatus.FAILED)
    Job.create(stage=stage, status=JobStatus.SUCCESS)
    Job.create(stage=stage, status=JobStatus.FAILED)
    assert Stage.get(Stage.id == stage.id).status is StageStatus.FAILED
    assert Build.get(Build.id == build.id).status is BuildStatus.FAILED


def test_2(connection):
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='a', order=1, build=build)

    Job.create(stage=stage, status=JobStatus.RUNNING)
    Job.create(stage=stage, status=JobStatus.RUNNING)
    Job.create(stage=stage, status=JobStatus.FAILED)
    stage.status = StageStatus.CANCELED
    stage.save()
    jobs = list(Job.select().where(Job.stage == stage))
    assert jobs[0].status is JobStatus.CANCELED
    assert jobs[1].status is JobStatus.CANCELED
    assert jobs[2].status is JobStatus.FAILED
