from enum import Enum

from peewee import CharField
from peewee import ForeignKeyField
from peewee import PrimaryKeyField

from piper_driver.models.base_model import BaseModel
from piper_driver.models.fields import EnumField
from piper_driver.models.user_model import User


class ProjectRole(Enum):
    MASTER = 1
    DEVELOPER = 2
    GUEST = 3


class Project(BaseModel):
    id = PrimaryKeyField()
    origin = CharField(unique=True)
    url = CharField()
    pubkey = CharField(null=True)


class ProjectUser(BaseModel):
    role = EnumField(choices=ProjectRole)
    user = ForeignKeyField(User)
    project = ForeignKeyField(Project)

    class Meta:
        indexes = (
            (('project', 'user'), True),
        )
