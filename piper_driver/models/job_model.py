from enum import Enum
import re
from typing import Dict, Any, List
import os

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import CharField
from simpleeval import simple_eval, InvalidExpression

from piper_driver.models.base_model import BaseModel, database_proxy
from piper_driver.models.fields import EnumField, UuidField
from piper_driver.models.stage_model import Stage, StageStatus
from piper_driver.addins.exceptions import *
from piper_driver.addins.common import Common


class JobStatus(Enum):
    CREATED = 1
    READY = 2
    PENDING = 3
    RUNNING = 4
    FAILED = 5
    SUCCESS = 6
    CANCELED = 7
    SKIPPED = 8
    ERROR = 9

    def to_str(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, string: str):
        return cls.__getattr__(string.upper())


class ResponseJobStatus(Enum):
    OK = 'OK'
    CANCEL = 'CANCEL'
    ERROR = 'ERROR'


class RequestJobStatus(Enum):
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    ERROR = 'ERROR'


class JobError(Enum):
    STATUS_INVALID_TYPE = 'job.error.status.invalid-type'
    IMAGE_INVALID_TYPE = 'job.error.image.invalid-type'
    ONLY_INVALID_TYPE = 'job.error.only.invalid-type'
    SECRET_READ_ONLY = 'job.error.secret.read-only'


class Job(BaseModel):
    id = PrimaryKeyField()
    stage = ForeignKeyField(Stage, on_delete='CASCADE')
    group = CharField(default='all')
    status = EnumField(choices=JobStatus, default=JobStatus.CREATED)
    image = CharField()
    when = CharField(null=True)
    secret = UuidField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_status = self.status

    def save(self, force_insert=False, only=None):
        errors = list()
        if not self.validate(errors):
            print(errors)
            raise ModelInvalid(errors)

        if Job.status not in self.dirty_fields or not self.stage:
            return super().save(force_insert, only)

        with database_proxy.transaction() as txn:
            try:
                old = self.stage.status
                statuses = {x.status for x in
                            Job.select(Job.status).where((Job.stage == self.stage) & (Job.id != self.id))}
                statuses.add(self.status)

                severity = [
                    JobStatus.RUNNING,
                    JobStatus.PENDING,
                    JobStatus.CREATED,
                    JobStatus.READY,
                    JobStatus.ERROR,
                    JobStatus.FAILED,
                    JobStatus.CANCELED,
                    JobStatus.SKIPPED,
                    JobStatus.SUCCESS,
                ]

                for s in severity:
                    if s in statuses:
                        self.stage.status = StageStatus(s.value)

                self.stage.save(direct=False)
                return super(Job, self).save(force_insert, only)
            except Exception as e:
                self.stage.status = old
                txn.rollback()
                raise e

    def validate(self, errors=None) -> bool:
        if errors is None:
            errors = list()

        if self.group is not None:
            if not isinstance(self.group, str) or not re.match(r'^[a-zA-Z0-9_-]{1,254}$', self.group):
                errors.append('group')
        if not isinstance(self.status, JobStatus):
            errors.append('status')
        if not isinstance(self.image, str):
            errors.append('image')
        if self.when is not None and not isinstance(self.when, str):
            errors.append('when')

        return len(errors) == 0

    @property
    def environment(self) -> Dict[str, Any]:
        from piper_driver.models.environment_model import Environment
        names = dict()
        for env in Environment.select().where(Environment.job == self):
            names[env.name] = env.value

        return names

    @property
    def commands(self) -> List[str]:
        from piper_driver.models.command_model import Command
        commands = list()
        for command in Command.select().where(Command.job == self).order_by(Command.order.asc()):
            commands.append(command.cmd)

        return commands

    def evaluate_when(self) -> bool:
        env = self.environment
        try:
            return bool(simple_eval(self.when, names=env))
        except (InvalidExpression, SyntaxError, TypeError) as e:
            raise JobExpressionException()

    def export(self) -> Dict[Any, Any]:
        build = self.stage.build
        project = build.project
        export = {
            'image': self.image,
            'commands': self.commands,
            'repository': {
                'origin': project.origin,
                'branch': build.branch,
                'commit': build.commit,
            },
            'env': self.environment,
        }

        return export

    @property
    def log_path(self) -> str:
        path = os.path.join(Common.JOB_LOG_DIR, str(self.id))

        return path

    def read_log(self, offset: int=0, limit: int=100) -> bytes:
        with open(self.log_path, 'rb') as fp:
            if offset is not None:
                fp.seek(offset)
            data = fp.read() if limit is None else fp.read(limit)

        return data

    def append_log(self, contents) -> None:
        with open(self.log_path, mode='ab') as fp:
            fp.write(contents)
