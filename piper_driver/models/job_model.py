from enum import Enum

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import CharField

from piper_driver.addins.exceptions import *
from piper_driver.models.base_model import BaseModel, database_proxy
from piper_driver.models.fields import EnumField, RandomSecretField
from piper_driver.models.stage_model import Stage, StageStatus
from piper_driver.models.runner_group_model import RunnerGroup


class JobStatus(Enum):
    """
    CREATED -> PENDING | READY | CANCELED
    PENDING -> READY | CANCELED
    READY -> RUNNING | FAILED | SUCCESS |  CANCELED
    RUNNING -> RUNNING | FAILED | SUCCESS |  CANCELED
    FAILED -> CREATED
    """
    CREATED = 1
    PENDING = 2
    READY = 3
    RUNNING = 4
    FAILED = 5
    SUCCESS = 6
    CANCELED = 7


class JobError(Enum):
    STATUS_INVALID_TYPE = 'job.error.status.invalid-type'
    IMAGE_INVALID_TYPE = 'job.error.image.invalid-type'
    ONLY_INVALID_TYPE = 'job.error.only.invalid-type'
    SECRET_READ_ONLY = 'job.error.secret.read-only'


class Job(BaseModel):
    id = PrimaryKeyField()
    stage = ForeignKeyField(Stage)
    group = ForeignKeyField(RunnerGroup, null=True)
    status = EnumField(choices=JobStatus, default=JobStatus.CREATED)
    image = CharField(null=True)
    only = CharField(null=True)
    secret = RandomSecretField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_status = self.status

    def validate(self, errors=None):
        if errors is None:
            errors = set()

        if self.status is not None and not isinstance(self.status, JobStatus):
            errors.add(JobError.STATUS_INVALID_TYPE)

        if self.image is not None and not isinstance(self.image, str):
            errors.add(JobError.IMAGE_INVALID_TYPE)

        if self.only is not None and not isinstance(self.only, str):
            errors.add(JobError.ONLY_INVALID_TYPE)

        return len(errors) == 0


