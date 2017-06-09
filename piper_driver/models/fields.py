import uuid
import pickle

from peewee import Field


class EnumField(Field):
    db_field = 'int'

    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return self.choices(value)


class UuidField(Field):
    db_field = 'uuid'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = uuid.uuid4

    def db_value(self, value):
        return str(value)

    def python_value(self, value):
        return uuid.UUID(value)


class PickleField(Field):
    db_field = 'varchar(255)'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def db_value(self, value):
        return pickle.dumps(value)

    def python_value(self, value):
        return pickle.loads(value)
