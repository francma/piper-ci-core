import uuid
from enum import Enum

from peewee import PrimaryKeyField, TextField
from peewee import CharField

from piper_core.model.fields import EnumField
from piper_core.model.base_model import BaseModel


class UserRole(Enum):
    MASTER = 1
    ADMIN = 2
    NORMAL = 3
    GUEST = 4

    def to_str(self) -> str:
        return self.name.lower()

    @staticmethod
    def from_str(string: str) -> 'UserRole':
        return UserRole.__getattr__(string.upper())  # type: ignore

    def __str__(self):
        return self.name.lower()


class User(BaseModel):
    id = PrimaryKeyField()
    role: UserRole = EnumField(choices=UserRole)
    email = CharField(unique=True)
    token = CharField(unique=True, default=lambda: uuid.uuid4().hex)
    public_key = TextField(unique=True)

    @classmethod
    def create(cls, **query) -> 'User':
        return super().create(**query)
