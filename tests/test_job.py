import json
import tempfile

import pytest

from piper_driver.models import *
from piper_driver.app import app
from piper_driver.addins.exceptions import *
from piper_driver.addins.common import Common
from http import HTTPStatus

app.testing = True


def test_job_evaluate_condition(connection):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='master', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)

    when = 'BOOL_VAR'
    job = Job.create(stage=stage, image='IMAGE', when=when)
    Environment.create(name='BOOL_VAR', value=True, job=job)
    assert job.evaluate_when() is True

    when = 'STR_VAR == "string"'
    job = Job.create(stage=stage, image='IMAGE', when=when)
    Environment.create(name='STR_VAR', value='string', job=job)
    assert job.evaluate_when() is True

    when = 'INT_VAR % 2 == 0'
    job = Job.create(stage=stage, image='IMAGE', when=when)
    Environment.create(name='INT_VAR', value=22, job=job)
    assert job.evaluate_when() is True

    when = 'INT_VAR %%%%% 2 == 0'
    job = Job.create(stage=stage, image='IMAGE', when=when)
    Environment.create(name='INT_VAR', value=22, job=job)
    with pytest.raises(JobExpressionException):
        job.evaluate_when()


def test_model(connection):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)

    job = Job()
    job.stage = stage
    job.image = 1
    job.when = 1
    job.status = 1
    with pytest.raises(ModelInvalid) as e:
        job.save()
    expected = set(['status', 'image', 'when'])
    assert set(e.value.errors) == expected
    errors = list()
    job.validate(errors)
    assert set(errors) == expected

    job.image = 'image'
    job.when = '1 == 1'
    job.status = JobStatus.CREATED
    assert job.validate()
    job.save()


def test_queue(connection, redis):
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    runner1 = Runner.create(group='1')
    runner2 = Runner.create(group='2')

    build = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', group='2')
    JobQueue.push(job)

    assert JobQueue.pop(runner1) is None
    assert JobQueue.pop(runner2) == job
    assert JobQueue.pop(runner2) is None


def test_job_runner_export(connection):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)

    job = Job.create(stage=stage, image='IMAGE')
    Command.create(order=1, job=job, cmd='1')
    Command.create(order=2, job=job, cmd='2')
    Command.create(order=3, job=job, cmd='3')
    Command.create(order=4, job=job, cmd='4')

    Environment.create(name='a', value='a', job=job)
    Environment.create(name='b', value='b', job=job)
    Environment.create(name='c', value='c', job=job)

    with open('tests/runner_exports/export_1.json') as fp:
        expected = json.load(fp)
    assert job.export() == expected

    job = Job.create(stage=stage, image='IMAGE')
    Command.create(order=1, job=job, cmd='1')
    Command.create(order=2, job=job, cmd='2')
    Command.create(order=3, job=job, cmd='3')
    Command.create(order=4, job=job, cmd='4')

    with open('tests/runner_exports/export_2.json') as fp:
        expected = json.load(fp)
    assert job.export() == expected


def test_log_write(connection):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', status=JobStatus.RUNNING)

    with tempfile.TemporaryDirectory() as tempdir:
        Common.JOB_LOG_DIR = tempdir
        client = app.test_client()
        r = client.post('/jobs/report/' + str(job.secret) + '?status=' + RequestJobStatus.RUNNING.value, data='12')
        assert r.status_code == 200
        r = client.post('/jobs/report/' + str(job.secret) + '?status=' + RequestJobStatus.RUNNING.value, data='34')
        assert r.status_code == 200
        r = client.post('/jobs/report/' + str(job.secret) + '?status=' + RequestJobStatus.COMPLETED.value, data='5')
        assert r.status_code == 200

        with open(job.log_path) as fp:
            assert fp.read() == '12345'

        job = Job.get(Job.id == job.id)
        assert job.status is JobStatus.SUCCESS


def test_log_read(connection):
    user1 = User.create(role=UserRole.MASTER, email='2@email.com')
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', status=JobStatus.RUNNING)
    with tempfile.TemporaryDirectory() as tempdir:
        Common.JOB_LOG_DIR = tempdir
        client = app.test_client()

        job.append_log(b'123')
        r = client.get('/jobs/' + str(job.id) + '/log', headers={
            'Authorization': 'Bearer ' + str(user1.token),
        })
        assert r.status_code == HTTPStatus.OK
        assert r.data == b'123'

        job.append_log(b'456')
        r = client.get('/jobs/' + str(job.id) + '/log', headers={
            'Authorization': 'Bearer ' + str(user1.token),
            'Range': 'bytes 3-5',
        })
        assert r.status_code == HTTPStatus.PARTIAL_CONTENT
        assert r.data == b'45'




