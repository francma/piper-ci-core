from piper_driver.app import app
from piper_driver.models import *

app.testing = True


def test_first(connection, monkeypatch):
    client = app.test_client()
    project = Project.create(url='https://A', origin='https://github.com/francma/piper-ci-test-repo.git')
    group = RunnerGroup.create(name='RUNNER')

    with open('tests/webhooks/github_push_1.json') as fd:
        contents = fd.read()

    with open('tests/configs/github_push_1.yml', encoding='utf-8') as fd:
        yml = fd.read()

    monkeypatch.setattr('piper_driver.addins.github.fetch_piper_yml', lambda x: yml)

    r = client.post('webhook', data=contents, content_type='application/json')
    assert r.status_code == 200

    builds = Build.select().where(Build.project == project)
    builds = list(builds)
    assert len(builds) == 1

    build = builds[0]
    assert build.project == project
    assert build.ref == 'refs/heads/master'
    assert build.commit == 'd9346cf45f551bce7f02c810e44fbc9776734baf'

    stages = Stage.select().where(Stage.build == build).order_by(Stage.order.asc())
    stages = list(stages)
    assert len(stages) == 2
    assert stages[0].name == 'one'
    assert stages[0].order == 0
    assert stages[0].build == build

    assert stages[1].name == 'two'
    assert stages[1].order == 1
    assert stages[1].build == build

    jobs = Job.select().where(Job.stage == stages[0])
    jobs = list(jobs)
    assert len(jobs) == 1
    job = jobs[0]
    assert job.stage == stages[0]
    assert job.status == JobStatus.CREATED
    assert job.group == group
    assert job.image == 'IMAGE'
    assert job.only == '$PIPER_BRANCH == master'

    # for env in Environment.select().where(Environment.job == job):
    #     print(env.type)
    #     print(env.value)
    # assert 0
