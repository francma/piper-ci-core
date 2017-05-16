from enum import Enum
import re
import datetime

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import FixedCharField
from peewee import CharField
from peewee import DateTimeField

from piper_driver.addins.exceptions import *
from piper_driver.models.base_model import BaseModel
from piper_driver.models.fields import EnumField
from piper_driver.models.project_model import Project


class BuildStatus(Enum):
    CREATED = 1
    PENDING = 2
    READY = 3
    RUNNING = 4
    FAILED = 5
    SUCCESS = 6
    CANCELED = 7

    def to_str(self):
        return self.name.lower()

    @staticmethod
    def from_str(string: str):
        return BuildStatus.__getattr__(string.upper())


class Build(BaseModel):
    id = PrimaryKeyField()
    project = ForeignKeyField(Project)
    ref = CharField()
    commit = FixedCharField(max_length=40)
    status = EnumField(choices=BuildStatus, default=BuildStatus.CREATED)
    created = DateTimeField(default=datetime.datetime.now)

    # @property
    # def commit(self) -> str:
    #     return self._commit
    #
    # @property
    # def status(self) -> BuildStatus:
    #     return self._status
    #
    # @status.setter
    # def status(self, value: BuildStatus) -> None:
    #     if not isinstance(value, BuildStatus):
    #         raise ModelInvalid()
    #     self._status = value
    #
    # @commit.setter
    # def commit(self, value: str) -> None:
    #     if not isinstance(value, str):
    #         raise ModelInvalid
    #     value = value.lower()
    #     if not re.match(r'^[a-f0-9]{40}$', value):
    #         raise ModelInvalid
    #
    #     self._commit = value
    #
    # @property
    # def ref(self) -> str:
    #     return self._ref
    #
    # @ref.setter
    # def ref(self, value: str) -> None:
    #     if not isinstance(value, str):
    #         raise ModelInvalid()
    #     self._ref = value
