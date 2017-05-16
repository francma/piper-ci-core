from functools import wraps

import flask
from flask_uwsgi_websocket import WebSocket
from peewee import MySQLDatabase

from piper_driver.repository import *
from piper_driver.addins import github
from piper_driver.models import *

app = flask.Flask(__name__)
ws = WebSocket(app)

app.config['DATABASE_NAME'] = 'piper_driver'
app.config['DATABASE_USER'] = 'root'
app.config['DATABASE_PASSWORD'] = 'chleba11'
app.config['SECRET_KEY'] = 'SECRET'


def get_db():
    if not hasattr(flask.g, 'database'):
        database = MySQLDatabase(
            app.config['DATABASE_NAME'], user=app.config['DATABASE_USER'], password=app.config['DATABASE_PASSWORD']
        )
        flask.g.database = database

    return flask.g.database


@app.teardown_request
def _db_close(exc):
    if hasattr(flask.g, 'database'):
        flask.g.database.close()


def after_this_request(func):
    if not hasattr(flask.g, 'call_after_request'):
        flask.g.call_after_request = []
    flask.g.call_after_request.append(func)

    return func


@app.after_request
def per_request_callbacks(response):
    for func in getattr(flask.g, 'call_after_request', ()):
        result = func(response)
        if result is not None:
            response = result
    return response


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):
            if 'Authorization' not in flask.request.headers:
                flask.abort(401)

            user = None
            data = flask.request.headers['Authorization']
            token = str.replace(data, 'Bearer ', '')
            try:
                user = User.get(User.token == token)
            except:
                flask.abort(401)

            return f(user, *args, **kws)
    return decorated_function


_repositories = {
    'build': BuildRepository,
    'job': JobRepository,
    'stage': StageRepository,
    'identity': IdentityRepository,
}


@app.route('/build')
@app.route('/build/<int:idx>')
@authorize
def build(user, idx=None):
    prefix = flask.request.path[1:]
    prefix = prefix[:prefix.find('/')]
    repo = _repositories[prefix]
    method = flask.request.method

    if idx and method == 'GET':
        method = 'LIST'

    if method == 'PUT':
        data = flask.request.get_json()
        repo.update(idx, data, user)
        return '', 204

    if method == 'POST':
        data = flask.request.get_json()
        repo.create(idx, data, user)
        return '', 201

    if method == 'GET':
        return flask.jsonify(repo.get(idx, user))

    if method == 'DELETE':
        repo.delete(idx, user)
        return '', 204

    if method == 'LIST':
        params = flask.request.args.items()
        if 'limit' in params:
            limit = params['limit']
            del params['limit']
        else:
            limit = 10

        if 'offset' in params:
            offset = params['offset']
            del params['offset']
        else:
            offset = 0

        if 'order' in params:
            order = params['order'].split(',')
            del params['order']
        else:
            order = []

        filters = params

        return flask.jsonify(repo.list(filters, order, limit, offset, user))


@app.route('/webhook', methods=['POST'])
def webhook():
    data = flask.request.get_json()
    if not data:
        flask.abort(400)
        return

    commits = github.parse_webhook(data)
    if len(commits) == 0:
        flask.abort(400)
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
        load_config(build, yml)
        # add GIT variables to ENV
        for job in Job.select().join(Stage).where(Stage.build == build):
            Environment.create(name='PIPER', value=True, job=job)
            Environment.create(name='PIPER_BRANCH', value=commit.branch.ref, job=job)
            Environment.create(name='PIPER_COMMIT', value=commit.sha, job=job)
            Environment.create(name='PIPER_COMMIT_MESSAGE', value=commit.message, job=job)
            Environment.create(name='PIPER_JOB_ID', value=job.id, job=job)
            Environment.create(name='PIPER_BUILD_ID', value=build.id, job=job)
            Environment.create(name='PIPER_STAGE', value=job.stage.name, job=job)

    return ''
