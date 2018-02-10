from peewee import PrimaryKeyField, ForeignKeyField, CharField
from piper_core.model.fields import PickledField
from typing import Union

from piper_core.model.base_model import BaseModel
from piper_core.model.jobs.job import Job


class Environment(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    value: Union[str, int, bool] = PickledField()
    job: Job = ForeignKeyField(Job, on_delete='CASCADE')

    @classmethod
    def create(cls, **query) -> 'Environment':
        return super().create(**query)
