from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import CharField
from peewee import IntegerField

from piper_driver.models.base_model import BaseModel
from piper_driver.models.job_model import Job


class Command(BaseModel):
    id = PrimaryKeyField()
    order = IntegerField()
    cmd = CharField()
    job = ForeignKeyField(Job, on_delete='CASCADE')
