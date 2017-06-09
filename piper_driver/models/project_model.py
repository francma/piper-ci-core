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

    def to_str(self):
        return self.name.lower()

    @staticmethod
    def from_str(string: str):
        return getattr(ProjectRole, string.upper())


class Project(BaseModel):
    id = PrimaryKeyField()
    origin = CharField(unique=True, max_length=128)
    url = CharField()
    pubkey = CharField(null=True)


class ProjectUser(BaseModel):
    role = EnumField(choices=ProjectRole)
    user = ForeignKeyField(User, on_delete='CASCADE')
    project = ForeignKeyField(Project, on_delete='CASCADE')

    class Meta:
        indexes = (
            (('project', 'user'), True),
        )
