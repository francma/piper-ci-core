import json
from http import HTTPStatus

import pytest
from pathlib import Path

from piper_core.model import *
from piper_core.utils.exceptions import *
from piper_core.container import Container


def test_job_evaluate_condition(container: Container):
    assert container
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='master', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)

    only = 'BOOL_VAR'
    job = Job.create(stage=stage, image='IMAGE', only=only)
    Environment.create(name='BOOL_VAR', value=True, job=job)
    assert job.evaluate_only() is True

    only = 'STR_VAR == "string"'
    job = Job.create(stage=stage, image='IMAGE', only=only)
    Environment.create(name='STR_VAR', value='string', job=job)
    assert job.evaluate_only() is True

    only = 'INT_VAR % 2 == 0'
    job = Job.create(stage=stage, image='IMAGE', only=only)
    Environment.create(name='INT_VAR', value=22, job=job)
    assert job.evaluate_only() is True

    only = 'INT_VAR %%%%% 2 == 0'
    job = Job.create(stage=stage, image='IMAGE', only=only)
    Environment.create(name='INT_VAR', value=22, job=job)
    with pytest.raises(JobExpressionException):
        job.evaluate_only()


def test_queue(container: Container):
    assert container
    project1 = Project.create(url='https://1', origin='https://github.com/francma/piper-ci-test-repo.git')
    runner1 = Runner.create(group='1', token='ABC')
    runner2 = Runner.create(group='2', token='DEF')

    build = Build.create(project=project1, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', group='2')

    queue = container.get_job_queue()
    queue.push(job)

    assert queue.pop(runner1) is None
    assert queue.pop(runner2) == job
    assert queue.pop(runner2) is None


def test_job_runner_export(container: Container):
    assert container
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
        expected['secret'] = job.secret
    assert job.export() == expected

    job = Job.create(stage=stage, image='IMAGE')
    Command.create(order=1, job=job, cmd='1')
    Command.create(order=2, job=job, cmd='2')
    Command.create(order=3, job=job, cmd='3')
    Command.create(order=4, job=job, cmd='4')

    with open('tests/runner_exports/export_2.json') as fp:
        expected = json.load(fp)
        expected['secret'] = job.secret
    assert job.export() == expected


def test_log_write(container: Container):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', status=Status.RUNNING)
    command1 = Command.create(job=job, order=0, cmd='echo Hello!')
    command2 = Command.create(job=job, order=1, cmd='echo Hello!')

    command1_start = '::piper:command:0:start:1512383889::\n'
    command1_content = 'Hello!'
    command1_end = '\n::piper:command:0:end:1512383890:0::\n'

    command2_start = '::piper:command:1:start:1512383891::\n'
    command2_content = 'Hello!'
    command2_end = '\n::piper:command:1:end:1512383892:0::\n'

    messages = [
        command1_start + command1_content + command1_end,
        command2_start,
        command2_content,
        command2_end,
    ]

    app = container.get_app()
    app.testing = True
    client = app.test_client()
    r = client.post('/jobs/report/' + str(job.secret) + '?status=' + RequestStatus.RUNNING.value, data=messages[0])
    assert r.status_code == 200
    command1 = Command.get(Command.id == command1.id)
    assert command1.log_start == len(command1_start)
    assert command1.log_end == len(command1_start) + len(command1_content)
    assert command1.start.timestamp() == 1512383889
    assert command1.end.timestamp() == 1512383890
    assert command1.return_code == 0

    r = client.post('/jobs/report/' + str(job.secret) + '?status=' + RequestStatus.RUNNING.value, data=messages[1])
    assert r.status_code == 200
    command2 = Command.get(Command.id == command2.id)
    assert command2.log_start == len(messages[0]) + len(command2_start)
    assert command2.log_end is None
    assert command2.start.timestamp() == 1512383891
    assert command2.end is None
    assert command2.return_code is None

    r = client.post('/jobs/report/' + str(job.secret) + '?status=' + RequestStatus.RUNNING.value, data=messages[2])
    assert r.status_code == 200
    command2 = Command.get(Command.id == command2.id)
    assert command2.log_start == len(messages[0]) + len(command2_start)
    assert command2.log_end is None
    assert command2.start.timestamp() == 1512383891
    assert command2.end is None
    assert command2.return_code is None

    r = client.post('/jobs/report/' + str(job.secret) + '?status=' + RequestStatus.COMPLETED.value, data=messages[3])
    assert r.status_code == 200
    command2 = Command.get(Command.id == command2.id)
    assert command2.log_start == len(messages[0]) + len(command2_start)
    assert command2.log_end == len(messages[0]) + len(command2_start) + len(command2_content)
    assert command2.start.timestamp() == 1512383891
    assert command2.end.timestamp() == 1512383892
    assert command2.return_code == 0

    job_log_dir = Path(container.config['app']['job_log_dir'])
    with open(job_log_dir / (str(job.id) + job.secret)) as fp:
        assert fp.read() == ''.join(messages)

    job = Job.get(Job.id == job.id)
    assert job.status is Status.SUCCESS


def test_log_read(container: Container):
    user1 = User.create(role=UserRole.MASTER, email='2@email.com', public_key='AAA')
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage = Stage.create(name='first', order=1, build=build)
    job = Job.create(stage=stage, image='IMAGE', status=Status.RUNNING)

    app = container.get_app()
    facade = container.get_jobs_facade()
    app.testing = True

    facade.append_log(job, b'123')
    assert facade.read_log(user1, job.id) == b'123'
    with app.test_client() as client:
        r = client.get('/jobs/' + str(job.id) + '/log')
        assert r.status_code == HTTPStatus.OK
        assert r.data == b'123'

    facade.append_log(job, b'456')
    assert facade.read_log(user1, job.id, 3, 2) == b'45'
    with app.test_client() as client:
        r = client.get('/jobs/' + str(job.id) + '/log', headers={
            'Range': 'bytes 3-5',
        })

        assert r.status_code == HTTPStatus.PARTIAL_CONTENT
        assert r.data == b'45'


def test_status(container: Container):
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    build = Build.create(project=project, branch='a', commit='634721d9da222050d41dce164d9de35fe475aa7a')
    stage1 = Stage.create(name='first', order=1, build=build)
    Job.create(stage=stage1, image='IMAGE')
    Job.create(stage=stage1, image='IMAGE')
    Job.create(stage=stage1, image='IMAGE')
    stage2 = Stage.create(name='first', order=2, build=build)
    Job.create(stage=stage2, image='IMAGE')
    Job.create(stage=stage2, image='IMAGE')
    Job.create(stage=stage2, image='IMAGE')
    stage3 = Stage.create(name='first', order=3, build=build)
    Job.create(stage=stage3, image='IMAGE')
    Job.create(stage=stage3, image='IMAGE')
    Job.create(stage=stage3, image='IMAGE')

    stage1.status = Status.READY
    stage1.save()

    stage1.status = Status.RUNNING
    stage1.save()
    assert Stage.get(Stage.id == stage2).status is Status.PENDING
    assert Stage.get(Stage.id == stage3).status is Status.PENDING
    for job in Job.select().where(Job.stage == stage2 | Job.stage == stage3):
        assert job.status is Status.PENDING

    with container.get_db().atomic():
        for job in Job.select().where(Job.stage == stage1):
            job.status = Status.SUCCESS
            job.save()

    assert Stage.get(Stage.id == stage2).status is Status.READY
    for job in Job.select().where(Job.stage == stage2):
        assert job.status is Status.READY
