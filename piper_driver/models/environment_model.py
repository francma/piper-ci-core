from typing import Union
import pickle
import re

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import CharField

from piper_driver.addins.exceptions import *
from piper_driver.models.base_model import BaseModel
from piper_driver.models.job_model import Job


class Environment(BaseModel):
    id = PrimaryKeyField()
    _name = CharField()
    _value = CharField()
    job = ForeignKeyField(Job)

    @property
    def value(self) -> None:
        return pickle.loads(self._value)

    @value.setter
    def value(self, value: Union[int, str, bool]):
        if type(value) not in [int, str, bool]:
            raise ModelInvalidValueException('Type {} is not supported'.format(type(value)))
        self._value = pickle.dumps(value)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value) or len(value) > 255:
            raise ModelInvalidValueException('Invalid name for environment variable.')
        self._name = value
