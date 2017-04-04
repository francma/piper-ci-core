from enum import Enum

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import CharField
from peewee import IntegerField

from piper_driver.models.base_model import BaseModel
from piper_driver.models.fields import EnumField
from piper_driver.models.build_model import Build


class StageStatus(Enum):
    NEW = 1
    WAITING = 2
    ERROR = 3


class Stage(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    order = IntegerField()
    build = ForeignKeyField(Build)
    status = EnumField(choices=StageStatus, default=StageStatus.NEW)
