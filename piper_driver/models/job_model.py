from enum import Enum

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import CharField

from piper_driver.addins.exceptions import *
from piper_driver.models.base_model import BaseModel
from piper_driver.models.fields import EnumField, RandomSecretField
from piper_driver.models.stage_model import Stage
from piper_driver.models.runner_group_model import RunnerGroup


class JobStatus(Enum):
    NEW = 1
    IN_QUEUE = 2
    SENT = 3
    RUNNING = 4
    ERROR = 5
    COMPLETED = 6


class Job(BaseModel):
    id = PrimaryKeyField()
    stage = ForeignKeyField(Stage)
    group = ForeignKeyField(RunnerGroup, null=True)
    _status = EnumField(choices=JobStatus, default=JobStatus.NEW)
    _image = CharField(null=True)
    _only = CharField(null=True)
    _secret = RandomSecretField()

    @property
    def secret(self) -> str:
        return self._secret

    @secret.setter
    def secret(self, value):
        raise RuntimeError('Secret property can not be set!')

    @property
    def image(self) -> str:
        return self._image

    @image.setter
    def image(self, value: str) -> None:
        if not isinstance(value, str):
            raise ModelInvalidValueException
        self._image = value

    @property
    def only(self) -> str:
        return self._only

    @only.setter
    def only(self, value: str) -> None:
        if not isinstance(value, str):
            raise ModelInvalidValueException
        self._only = value

    @property
    def status(self) -> JobStatus:
        return self._status

    @status.setter
    def status(self, value: JobStatus) -> None:
        if not isinstance(value, JobStatus):
            raise ModelInvalidValueException
        self._status = value



