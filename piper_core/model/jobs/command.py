from enum import Enum
from peewee import CharField
from peewee import ForeignKeyField
from peewee import IntegerField
from peewee import PrimaryKeyField, BigIntegerField, TimestampField
from typing import Union

from piper_core.model.fields import EnumField
from piper_core.model.base_model import BaseModel
from piper_core.model.jobs.job import Job


class CommandType(Enum):
    NORMAL = 1
    AFTER_FAILURE = 2

    def to_str(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, string: str):
        return cls.__getattr__(string.upper())  # type: ignore


class Command(BaseModel):
    id = PrimaryKeyField()
    order = IntegerField()
    cmd = CharField()
    type: CommandType = EnumField(choices=CommandType, default=CommandType.NORMAL)
    job: Job = ForeignKeyField(Job, on_delete='CASCADE')
    log_start = BigIntegerField(null=True, default=None)
    log_end = BigIntegerField(null=True, default=None)
    start = TimestampField(null=True, default=None)
    end = TimestampField(null=True, default=None)
    return_code = IntegerField(null=True, default=None)

    @classmethod
    def create(cls, **query) -> 'Command':
        return super().create(**query)
