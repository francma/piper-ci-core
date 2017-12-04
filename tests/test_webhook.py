import yaml

from piper_core.model import *
from piper_core.container import Container
from piper_core.utils.github import Github


def test_1(container: Container, monkeypatch):
    monkeypatch.setattr(Github, 'fetch_piper_yml', lambda x, y: yml)
    app = container.get_app()
    app.testing = True
    client = app.test_client()

    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')

    with open('tests/webhooks/github_push_1.json') as fd:
        contents = fd.read()

    with open('tests/configs/github_push_1.yml', encoding='utf-8') as fd:
        yml = yaml.load(fd)

    r = client.post('/webhook', data=contents, content_type='application/json')
    assert r.status_code == 200

    builds = Build.select().where(Build.project == project)
    builds = list(builds)
    assert len(builds) == 1

    build = builds[0]
    assert build.project == project
    assert build.branch == 'master'
    assert build.commit == 'd9346cf45f551bce7f02c810e44fbc9776734baf'

    stages = Stage.select().where(Stage.build == build).order_by(Stage.order.asc())
    stages = list(stages)
    assert len(stages) == 2
    assert stages[0].name == 'one'
    assert stages[0].order == 0
    assert stages[0].build == build
    # assert stages[0].status == Status.READY

    assert stages[1].name == 'two'
    assert stages[1].order == 1
    assert stages[1].build == build
    # assert stages[1].status == Status.PENDING
