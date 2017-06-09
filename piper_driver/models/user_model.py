from enum import Enum
import re

from peewee import PrimaryKeyField
from peewee import CharField

from piper_driver.addins.exceptions import *
from piper_driver.models.fields import EnumField, UuidField
from piper_driver.models.base_model import BaseModel


class UserRole(Enum):
    MASTER = 1
    ADMIN = 2
    NORMAL = 3

    def to_str(self):
        return self.name.lower()

    @staticmethod
    def from_str(string: str):
        return UserRole.__getattr__(string.upper())


class User(BaseModel):
    id = PrimaryKeyField()
    role = EnumField(choices=UserRole)
    email = CharField(unique=True, max_length=128)
    token = UuidField()
    public_key = CharField(null=True)

    # @property
    # def email(self) -> str:
    #     return self._email
    #
    # @email.setter
    # def email(self, value: str) -> None:
    #     if not isinstance(value, str):
    #         raise ModelInvalid()
    #     if not re.match(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', value):
    #         raise ModelInvalid('Expected email, got "{}"'.format(value))
    #     self._email = value
    #
    # @property
    # def role(self) -> UserRole:
    #     return self._role
    #
    # @role.setter
    # def role(self, value: UserRole) -> None:
    #     if not isinstance(value, UserRole):
    #         raise ModelInvalid()
    #     self._role = value
