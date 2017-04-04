import flask
import flask_restful
from flask_uwsgi_websocket import WebSocket
from peewee import MySQLDatabase
from flask_jwt_extended import JWTManager

from piper_driver.presenters.project import ProjectPresenter, ProjectPresenterList
from piper_driver.presenters.webhook import WebhookPresenter

app = flask.Flask(__name__)
ws = WebSocket(app)
api = flask_restful.Api(app)
jwt = JWTManager(app)

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


api.add_resource(ProjectPresenterList, '/project')
api.add_resource(ProjectPresenter, '/project/<int:project_id>')
api.add_resource(WebhookPresenter, '/webhook')
