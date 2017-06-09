from peewee import PrimaryKeyField, ForeignKeyField, CharField

from piper_driver.addins.exceptions import *
from piper_driver.models.base_model import BaseModel
from piper_driver.models.job_model import Job
from piper_driver.models.fields import PickleField


class Environment(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    value = PickleField()
    job = ForeignKeyField(Job, on_delete='CASCADE')

    def validate(self, errors=None):
        if errors is None:
            errors = list()

        if type(self.value) not in [int, str, bool]:
            errors.append('Type {} is not supported')

        return len(errors) == 0

    def save(self, force_insert=False, only=None):
        errors = list()
        if not self.validate(errors):
            raise ModelInvalid(errors)

        return super().save(force_insert, only)

