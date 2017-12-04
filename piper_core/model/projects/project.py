import datetime
from enum import Enum
from peewee import CharField, TextField, ForeignKeyField, PrimaryKeyField, DateTimeField
from typing import Union

from piper_core.model.base_model import BaseModel, database_proxy
from piper_core.model.fields import EnumField
from piper_core.model.users.user import User


class ProjectStatus(Enum):
    UNKNOWN = 1
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
        return cls.__getattr__(string.upper())  # type: ignore


class ProjectRole(Enum):
    MASTER = 1
    DEVELOPER = 2

    def to_str(self):
        return self.name.lower()

    @staticmethod
    def from_str(string: str):
        return getattr(ProjectRole, string.upper())  # type: ignore


class Project(BaseModel):
    id = PrimaryKeyField()
    origin = CharField(unique=True, max_length=128)
    url = CharField()
    status: ProjectStatus = EnumField(choices=ProjectStatus, default=ProjectStatus.UNKNOWN)
    created = DateTimeField(default=datetime.datetime.now)

    @classmethod
    def create(cls, **query) -> 'Project':
        return super().create(**query)


class ProjectUser(BaseModel):
    role = EnumField(choices=ProjectRole)
    user = ForeignKeyField(User, on_delete='CASCADE')
    project = ForeignKeyField(Project, on_delete='CASCADE')

    class Meta:
        indexes = (
            (('project', 'user'), True),
        )
