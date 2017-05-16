import json
import time

import pytest

from piper_driver.models import *
from piper_driver.addins.exceptions import *


def test_job_evaluate_condition(connection):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)

    only = 'BOOL_VAR'
    job = Job.create(stage=stage, image='IMAGE', only=only)
    Environment.create(name='BOOL_VAR', value=True, job=job)
    assert job_evaluate_condition(job) is True

    only = 'STR_VAR == "string"'
    job = Job.create(stage=stage, image='IMAGE', only=only)
    Environment.create(name='STR_VAR', value='string', job=job)
    assert job_evaluate_condition(job) is True

    only = 'INT_VAR % 2 == 0'
    job = Job.create(stage=stage, image='IMAGE', only=only)
    Environment.create(name='INT_VAR', value=22, job=job)
    assert job_evaluate_condition(job) is True

    only = 'INT_VAR %%%%% 2 == 0'
    job = Job.create(stage=stage, image='IMAGE', only=only)
    Environment.create(name='INT_VAR', value=22, job=job)
    with pytest.raises(JobOnlyExpressionException):
        job_evaluate_condition(job)


def test_model(connection):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)

    job = Job()
    job.stage = stage
    job.image = 1
    job.only = 1
    job.status = 1
    with pytest.raises(ModelInvalid) as e:
        job.save()
    expected = set([
        JobError.IMAGE_INVALID_TYPE,
        JobError.ONLY_INVALID_TYPE,
        JobError.STATUS_INVALID_TYPE,
    ])
    assert e.value.errors == expected
    errors = set()
    job.validate(errors)
    assert errors == expected

    job.image = 'image'
    job.only = '1 == 1'
    job.status = JobStatus.CREATED
    assert job.validate()
    job.save()


def test_queue(connection, redis):
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    project2 = Project.create(url='https://2', origin='git@github.com:francma/piper-ci-driver.git')

    group1 = RunnerGroup.create(name='group1')
    group2 = RunnerGroup.create(name='group2')

    runner1 = Runner.create(group=group1)
    runner2 = Runner.create(group=group2)
    runner3 = Runner.create()

    ProjectRunner.create(runner=runner1, project=project1)
    ProjectRunner.create(runner=runner1, project=project2)
    ProjectRunner.create(runner=runner2, project=project1)

    build = Build.create(project=project1, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', group=group2)
    job_queue_push(job)

    assert job_queue_pop(runner3) is None
    assert job_queue_pop(runner1) is None
    assert job_queue_pop(runner2) == job
    assert job_queue_pop(runner2) is None

    build = Build.create(project=project2, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', group=group2)
    job_queue_push(job)

    assert job_queue_pop(runner3) is None
    assert job_queue_pop(runner1) is None
    assert job_queue_pop(runner2) is None
    # FIXME there should be some warning if no runner can take the job (where? how? when?)

    build = Build.create(project=project2, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', group=group1)
    job_queue_push(job)

    assert job_queue_pop(runner3) is None
    assert job_queue_pop(runner2) is None
    assert job_queue_pop(runner1) == job
    assert job_queue_pop(runner1) is None


def test_job_runner_export(connection):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, ref='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)

    job = Job.create(stage=stage, image='IMAGE')
    Command.create(order=1, job=job, cmd='1')
    Command.create(order=2, job=job, cmd='2')
    Command.create(order=3, job=job, cmd='3')
    Command.create(order=4, job=job, cmd='4')

    Environment.create(name='a', value='a', job=job)
    Environment.create(name='b', value='b', job=job)
    Environment.create(name='c', value='c', job=job)

    export = job_runner_export(job)
    with open('tests/runner_exports/export_1.json') as fp:
        expected = json.load(fp)
    assert export == expected

    job = Job.create(stage=stage, image='IMAGE')
    Command.create(order=1, job=job, cmd='1')
    Command.create(order=2, job=job, cmd='2')
    Command.create(order=3, job=job, cmd='3')
    Command.create(order=4, job=job, cmd='4')

    export = job_runner_export(job)
    with open('tests/runner_exports/export_2.json') as fp:
        expected = json.load(fp)
    assert export == expected
