from enum import Enum

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import CharField
from peewee import IntegerField

from piper_driver.models.base_model import BaseModel, database_proxy
from piper_driver.models.fields import EnumField
from piper_driver.models.build_model import Build, BuildStatus


class StageStatus(Enum):
    """
    CREATED: all Job.status == JobStatus.CREATED
    PENDING: all Job.status in [JobStatus.PENDING, JobStatus.READY]
    RUNNING: exists Job.status == JobStatus.RUNNING
    FAILED: all Job.status in [JobStatus.FAILED, JobStatus.CANCELED]
    SUCCESS: all Job.status == JobStatus.SUCCESS
    CANCELED: all Job.status in [JobStatus.SUCCESS, JobStatus.CANCELED]
    """
    CREATED = 1
    PENDING = 2
    RUNNING = 4
    FAILED = 5
    SUCCESS = 6
    CANCELED = 7


class Stage(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    order = IntegerField()
    build = ForeignKeyField(Build)
    status = EnumField(choices=StageStatus, default=StageStatus.CREATED)


