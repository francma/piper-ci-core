from typing import Dict, Any, List, Union

import uuid
from enum import Enum
from peewee import CharField
from peewee import ForeignKeyField
from peewee import PrimaryKeyField
from simpleeval import simple_eval, InvalidExpression

from piper_core.utils.exceptions import *
from piper_core.model.base_model import BaseModel, database_proxy
from piper_core.model.fields import EnumField
from piper_core.model.stages.stage import Stage, Status


class ResponseStatus(Enum):
    OK = 'OK'
    CANCEL = 'CANCEL'
    ERROR = 'ERROR'


class RequestStatus(Enum):
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    ERROR = 'ERROR'


class Job(BaseModel):
    COMMAND_PREFIX = 'piper'
    COMMAND_BEGIN = '^::' + COMMAND_PREFIX + ':(command|after_failure):(\d+):start:(\d+)::$'
    COMMAND_END = '^::' + COMMAND_PREFIX + ':(command|after_failure):(\d+):end:(\d+):(\d+)::$'

    id: Union[int, PrimaryKeyField] = PrimaryKeyField()
    stage: Union[Stage, ForeignKeyField] = ForeignKeyField(Stage, on_delete='CASCADE')
    group: Union[str, CharField] = CharField(default='all')
    status: Union[EnumField, Status] = EnumField(choices=Status, default=Status.CREATED)
    image: Union[str, CharField] = CharField()
    only: Union[str, CharField, None] = CharField(null=True)
    secret: Union[CharField, str] = CharField(default=lambda: uuid.uuid4().hex)
    note: Union[str, CharField] = CharField(null=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_status = self.status

    @classmethod
    def create(cls, **query) -> 'Job':
        return super().create(**query)

    def save(self, force_insert=False, only=None):
        if Job.status not in self.dirty_fields or not self.stage:
            return super().save(force_insert, only)

        old = self.stage.status
        with database_proxy.transaction() as txn:
            try:
                statuses = {x.status for x in Job.select(Job.status).where(
                    (Job.stage == self.stage) & (Job.id != self.id)
                )}
                statuses.add(self.status)

                if statuses & {Status.ERROR}:
                    self.stage.status = Status.ERROR
                elif statuses & {Status.FAILED}:
                    self.stage.status = Status.FAILED
                elif statuses & {Status.RUNNING}:
                    self.stage.status = Status.RUNNING
                elif statuses & {Status.READY}:
                    if statuses & {Status.SUCCESS, Status.CANCELED, Status.SKIPPED}:
                        self.stage.status = Status.RUNNING
                    else:
                        self.stage.status = Status.READY
                elif statuses & {Status.SUCCESS}:
                    self.stage.status = Status.SUCCESS
                elif statuses & {Status.CANCELED}:
                    self.stage.status = Status.CANCELED
                elif statuses & {Status.SKIPPED}:
                    self.stage.status = Status.SKIPPED
                elif statuses & {Status.CREATED}:
                    self.stage.status = Status.CREATED

                self.stage.save()
                return super(Job, self).save(force_insert, only)
            except Exception as e:
                self.stage.status = old
                txn.rollback()
                raise e

    @property
    def environment(self) -> Dict[str, Any]:
        from piper_core.model.jobs.environment import Environment
        names = dict()
        for env in Environment.select().where(Environment.job == self):
            names[env.name] = env.value

        return names

    @property
    def commands(self) -> List[Any]:
        from piper_core.model.jobs.command import Command, CommandType

        commands = Command.select().where(
            (Command.job == self) & (Command.type == CommandType.NORMAL)
        ).order_by(Command.order.asc())

        return commands

    @property
    def after_failure(self) -> List[Any]:
        from piper_core.model.jobs.command import Command, CommandType

        commands = Command.select().where(
            (Command.job == self) & (Command.type == CommandType.AFTER_FAILURE)
        ).order_by(Command.order.asc())

        return commands

    def evaluate_only(self) -> bool:
        if self.only is None:
            return True

        env = self.environment
        try:
            return bool(simple_eval(self.only, names=env))
        except (InvalidExpression, SyntaxError, TypeError):
            raise JobExpressionException

    def export(self) -> Dict[Any, Any]:
        build = self.stage.build
        project = build.project
        export = {
            'image': self.image,
            'commands': [c.cmd for c in self.commands],
            'repository': {
                'origin': project.origin,
                'branch': build.branch,
                'commit': build.commit,
            },
            'env': self.environment,
            'secret': self.secret,
        }

        if self.after_failure:
            export['after_failure'] = [c.cmd for c in self.after_failure]

        return export
