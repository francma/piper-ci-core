import flask
from pathlib import Path

import peewee
import yaml
from http import HTTPStatus
from playhouse import db_url
from typing import Dict, Any, Union

from redis import Redis

from piper_core.model import *
from piper_core.blueprints import *
from piper_core.shell import PiperShell
from piper_core.utils.queue import Queue
from piper_core.utils.github import Github
from piper_core.utils.exceptions import *


class Container:

    def __init__(self, config: Dict[Any, Any]) -> None:
        self.config: Dict[Any, Any] = config
        self._builds_facade: BuildsFacade = None
        self._projects_facade: ProjectsFacade = None
        self._runners_facade: RunnersFacade = None
        self._stages_facade: StagesFacade = None
        self._users_facade: UsersFacade = None
        self._jobs_facade: JobsFacade = None
        self._db: peewee.Database = None
        self._queue: Queue = None
        self._job_queue: JobQueue = None
        self._app: flask.Flask = None
        self._shell: PiperShell = None
        self._schema = None
        self._github: Github = None

    def destroy(self):
        if self._db is not None:
            self._db.close()
            self._db = None

    def get_schema(self):
        if self._schema is None:
            cd = Path(__file__).parent.parent / 'openapi.yml'
            with cd.open('r') as fp:
                self._schema = yaml.load(fp)

        return self._schema

    def get_github(self):
        if self._github is None:
            self._github = Github(self.get_schema())

        return self._github

    def get_db(self):
        if self._db is None:
            self._db = db_url.connect(self.config['database']['dsn'])
            if isinstance(self._db, peewee.SqliteDatabase):
                self._db.execute_sql('PRAGMA foreign_keys=ON;')

        return self._db

    def get_queue(self) -> Queue:
        if self._queue is None:
            self._queue = Queue(Redis.from_url(self.config['queue']['url']))

        return self._queue

    def get_job_queue(self) -> JobQueue:
        if self._job_queue is None:
            self._job_queue = JobQueue(self.get_queue())

        return self._job_queue

    def get_jobs_facade(self) -> JobsFacade:
        if self._jobs_facade is None:
            self._jobs_facade = JobsFacade(Path(self.config['app']['job_log_dir']), self.get_job_queue())

        return self._jobs_facade

    def get_builds_facade(self) -> BuildsFacade:
        if self._builds_facade is None:
            self._builds_facade = BuildsFacade(self.get_job_queue(), self.get_schema(), self.get_github())

        return self._builds_facade

    def get_projects_facade(self) -> ProjectsFacade:
        if self._projects_facade is None:
            self._projects_facade = ProjectsFacade(self.get_schema())

        return self._projects_facade

    def get_runners_facade(self) -> RunnersFacade:
        if self._runners_facade is None:
            self._runners_facade = RunnersFacade(self.get_schema())

        return self._runners_facade

    def get_stages_facade(self) -> StagesFacade:
        if self._stages_facade is None:
            self._stages_facade = StagesFacade(self.get_job_queue())

        return self._stages_facade

    def get_users_facade(self) -> UsersFacade:
        if self._users_facade is None:
            self._users_facade = UsersFacade(self.get_schema())

        return self._users_facade

    def get_app(self) -> flask.Flask:
        if self._app is None:
            app = flask.Flask('piper')
            app.config['SECRET_KEY'] = self.config['app']['secret']

            app.register_blueprint(BuildBlueprintFactory.create(self.get_builds_facade()))
            app.register_blueprint(JobBlueprintFactory.create(self.get_jobs_facade(), self.get_job_queue()))
            app.register_blueprint(ProjectBlueprintFactory.create(self.get_projects_facade()))
            app.register_blueprint(RunnerBlueprintFactory.create(self.get_runners_facade()))
            app.register_blueprint(StageBlueprintFactory.create(self.get_stages_facade()))
            app.register_blueprint(IdentityBlueprintFactory.create(self.get_users_facade()))
            app.register_blueprint(WebhookBlueprintFactory.create(self.get_builds_facade()))
            app.register_blueprint(UserBlueprintFactory.create(self.get_users_facade()))

            @app.errorhandler(FacadeInvalidSchema)
            @app.errorhandler(FacadeInvalidAction)
            @app.errorhandler(WebhookParseException)
            def handle_bad(error: Union[FacadeInvalidSchema, FacadeInvalidAction]):
                return str(error), HTTPStatus.BAD_REQUEST

            @app.errorhandler(FacadeNotFound)
            def handle_not_found(error: FacadeNotFound):
                return str(error), HTTPStatus.NOT_FOUND

            @app.errorhandler(FacadeUnauthorized)
            def handle_unauthorized(error: FacadeUnauthorized):
                return str(error), HTTPStatus.UNAUTHORIZED

            @app.before_request
            def connect():
                self.init_db()

            @app.after_request
            def disconnect(response):
                self.close_db()

                return response

            self._app = app

        return self._app

    def get_shell(self, user: User):
        shell = PiperShell(user, self.get_users_facade(), self.get_builds_facade(), self.get_jobs_facade(),
                           self.get_projects_facade(), self.get_runners_facade(), self.get_stages_facade())

        return shell

    def init_db(self):
        database_proxy.initialize(self.get_db())

    def close_db(self):
        if self._db and not self._db.is_closed():
            self._db.close()
