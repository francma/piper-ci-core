from enum import Enum
import re

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import FixedCharField
from peewee import CharField

from piper_driver.addins.exceptions import *
from piper_driver.models.base_model import BaseModel
from piper_driver.models.fields import EnumField
from piper_driver.models.project_model import Project


class BuildStatus(Enum):
    NEW = 1
    WAITING = 2
    ERROR = 3
    FINISHED = 4


class Build(BaseModel):
    id = PrimaryKeyField()
    project = ForeignKeyField(Project)
    _ref = CharField()
    _commit = FixedCharField(max_length=40)
    _status = EnumField(choices=BuildStatus, default=BuildStatus.NEW)

    @property
    def commit(self) -> str:
        return self._commit

    @commit.setter
    def commit(self, value: str) -> None:
        if not isinstance(value, str):
            raise ModelInvalidValueException
        value = value.lower()
        if not re.match(r'^[a-f0-9]{40}$', value):
            raise ModelInvalidValueException

        self._commit = value

    @property
    def status(self) -> BuildStatus:
        return self._status

    @status.setter
    def status(self, value: BuildStatus) -> None:
        if not isinstance(value, BuildStatus):
            raise ModelInvalidValueException()
        self._status = value

    @property
    def ref(self) -> str:
        return self._ref

    @ref.setter
    def ref(self, value: str) -> None:
        if not isinstance(value, str):
            raise ModelInvalidValueException()
        self._ref = value
