from enum import Enum
import re

from peewee import PrimaryKeyField
from peewee import CharField

from piper_driver.addins.exceptions import *
from piper_driver.models.fields import EnumField
from piper_driver.models.base_model import BaseModel


class UserRole(Enum):
    ROOT = 1
    ADMIN = 2
    USER = 3


class User(BaseModel):
    id = PrimaryKeyField()
    _role = EnumField(choices=UserRole)
    _email = CharField(unique=True)

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str):
            raise ModelInvalidValueException()
        if not re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', value):
            raise ModelInvalidValueException('Expected email, got "{}"'.format(value))
        self._email = value

    @property
    def role(self) -> UserRole:
        return self._role

    @role.setter
    def role(self, value: UserRole) -> None:
        if not isinstance(value, UserRole):
            raise ModelInvalidValueException()
        self._role = value
