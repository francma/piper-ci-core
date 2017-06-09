from piper_driver.models import *
from piper_driver.addins.exceptions import *


def test_unknown_command(shell, connection):
    read, shell = shell
    assert not shell.onecmd('NOT A COMMAND')
    assert read() == '*** Unknown syntax: NOT A COMMAND\n'


def test_exit(shell):
    read, shell = shell
    assert shell.onecmd('exit')
    assert read() == 'Bye!\n'


def test_project(shell):
    read, shell = shell
    user1 = User.create(email='1@email.com', role=UserRole.MASTER)
    shell.user = user1
    project1 = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo1.git')
    project2 = Project.create(url='https://B', origin='https://github.com/francma/piper-ci-test-repo2.git')
    assert not shell.onecmd('project list')
    assert len(read())
    assert not shell.onecmd('project count')
    assert len(read())
    assert not shell.onecmd('project get 1')
    assert len(read())
    assert not shell.onecmd('project create url=https://C origin=https://github.com/francma/piper-ci-test-repo3.git')
    assert len(read())
    assert Project.get(Project.id == 3)
    assert not shell.onecmd('project update 3 url=https://D')
    assert Project.get(Project.id == 3).url == 'https://D'
    assert not shell.onecmd('project delete 3')
    assert Project.select().count() == 2
    assert not shell.onecmd('project user-add project=1 user=1 role=master')
    assert not shell.onecmd('project user-list')
    assert ProjectUser.select().where(ProjectUser.project == project1).count() == 1
    assert not shell.onecmd('project user-remove project=1 user=1')
    assert ProjectUser.select().where(ProjectUser.project == project1).count() == 0


def test_build(shell):
    read, shell = shell