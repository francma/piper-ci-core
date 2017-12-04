from peewee import PrimaryKeyField, CharField

from piper_core.model.base_model import BaseModel


class Runner(BaseModel):
    id = PrimaryKeyField()
    group = CharField()
    token = CharField()

    @classmethod
    def create(cls, **query) -> 'Runner':
        return super().create(**query)
