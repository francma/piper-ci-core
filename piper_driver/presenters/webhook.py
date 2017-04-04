import flask
from flask_restful import Resource, abort

from piper_driver.addins import github
from piper_driver.models import *


class WebhookPresenter(Resource):

    def post(self):
        data = flask.request.get_json()
        if not data:
            abort(400)
            return

        commits = github.parse_webhook(data)
        if len(commits) == 0:
            abort(400)
            return

        origin = commits[0].branch.repository.origin
        ref = commits[0].branch.ref
        project = Project.get(Project.origin == origin)
        for commit in commits:
            yml = github.fetch_piper_yml(commit)
            build = Build()
            build.project = project
            build.ref = ref
            build.commit = commit.sha
            build.status = BuildStatus.NEW
            load_config(build, yml)
            # add GIT variables to ENV
            for job in Job.select().join(Stage).where(Stage.build == build):
                Environment.create(name='PIPER', value=True, job=job)
                Environment.create(name='PIPER_BRANCH', value=commit.branch.ref, job=job)
                Environment.create(name='PIPER_COMMIT', value=commit.sha, job=job)
                Environment\
                    .create(name='PIPER_COMMIT_MESSAGE', value=commit.message, job=job)
                Environment.create(name='PIPER_JOB_ID', value=job.id, job=job)
                Environment.create(name='PIPER_BUILD_ID', value=build.id, job=job)
                Environment.create(name='PIPER_STAGE', value=job.stage.name, job=job)
