from peewee import PrimaryKeyField
from peewee import CharField

from piper_driver.models.base_model import BaseModel


class RunnerGroup(BaseModel):
    id = PrimaryKeyField()
    name = CharField(unique=True)

RunnerGroup.NONE_GROUP = RunnerGroup(name='none')
