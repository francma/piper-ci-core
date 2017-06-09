from peewee import PrimaryKeyField, CharField

from piper_driver.models.base_model import BaseModel
from piper_driver.models.fields import UuidField


class Runner(BaseModel):
    id = PrimaryKeyField()
    group = CharField()
    token = UuidField()
