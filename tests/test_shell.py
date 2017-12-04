from piper_core.model import *
from piper_core.container import Container


def test_unknown_command(shell):
    read, shell = shell
    assert not shell.onecmd('NOT A COMMAND')
    assert read() == '*** Unknown syntax: NOT A COMMAND\n'


def test_exit(shell):
    read, shell = shell
    assert shell.onecmd('exit')
    assert read() == 'Bye!\n'


def test_project(shell):
    read, shell = shell
    user1 = User.create(email='1@email.com', role=UserRole.MASTER, public_key='AAA')
    User.create(email='2@email.com', role=UserRole.NORMAL, public_key='AAB')
    shell.user = user1

    assert not shell.onecmd('project create url=https://C origin=https://github.com/francma/piper-ci-test-repo.git')
    assert len(read())
    assert not shell.onecmd('project list')
    assert len(read())
    assert not shell.onecmd('project count')
    assert len(read())
    assert not shell.onecmd('project get 1')
    assert len(read())

    assert not shell.onecmd('project update 1 url=https://D')
    assert Project.get(Project.id == 1).url == 'https://D'
    assert not shell.onecmd('project user-add project_id=1 user_id=2 role=master')
    assert not shell.onecmd('project user-list 1')
    assert ProjectUser.select().where(ProjectUser.project == 1).count() == 2
    assert not shell.onecmd('project user-remove project_id=1 user_id=2')
    assert ProjectUser.select().where(ProjectUser.project == 1).count() == 1
    assert not shell.onecmd('project delete 1')
    assert Project.select().count() == 0


def test_job_log(shell, container: Container):
    read, shell = shell
    user1 = User.create(email='1@email.com', role=UserRole.MASTER, public_key='AAA')
    shell.user = user1
    project1 = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo1.git')
    build = Build.create(project=project1, branch='master', commit='3f786850e387550fdab836ed7e6dc881de23001b')
    stage = Stage.create(build=build, order=0, name='stage1')
    job = Job.create(stage=stage, image='alpine')
    Command.create(order=0, cmd='echo Hello!', job=job)
    Command.create(order=1, cmd='echo Hello!', job=job)

    facade = container.get_jobs_facade()
    facade.append_log(job, 100 * b'ABC')
    assert not shell.onecmd('job log %d' % job.id)
    assert read() == 100 * 'ABC'
    facade.append_log(job, 100 * b'123')
    assert not shell.onecmd('job log %d' % job.id)
    assert read() == 100 * 'ABC' + 100 * '123'
