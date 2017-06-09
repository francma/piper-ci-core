import flask

from piper_driver.addins import github
from piper_driver.models import *

webhook_view = flask.Blueprint('webhook_view', __name__)


@webhook_view.route('/webhook', methods=['POST'])
def webhook():
    data = flask.request.get_json()
    if not data:
        flask.abort(400)
        return

    commit = github.parse_webhook(data)
    project = Project.get(Project.origin == commit.branch.repository.origin)
    yml = github.fetch_piper_yml(commit)
    build = Build(project=project, branch=commit.branch.name, commit=commit.sha)
    build.load_config(yml)

    jobs = Job.select().join(Stage).where(Stage.build == build)
    for job in jobs:
        Environment.create(name='PIPER', value=True, job=job)
        Environment.create(name='PIPER_BRANCH', value=commit.branch.name, job=job)
        Environment.create(name='PIPER_COMMIT', value=commit.sha, job=job)
        Environment.create(name='PIPER_COMMIT_MESSAGE', value=commit.message, job=job)
        Environment.create(name='PIPER_JOB_ID', value=job.id, job=job)
        Environment.create(name='PIPER_BUILD_ID', value=build.id, job=job)
        Environment.create(name='PIPER_STAGE', value=job.stage.name, job=job)

    stage = Stage.select().where(Stage.build == build).order_by(Stage.order.asc()).first()
    stage.status = StageStatus.READY
    stage.save()

    jobs = Job.select().where(Job.stage == stage)
    for job in jobs:
        JobQueue.push(job)

    return ''
