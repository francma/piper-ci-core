import re
import uuid

from peewee import Field


class EnumField(Field):
    db_field = 'int'

    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return self.choices(value)


class RandomSecretField(Field):
    db_field = 'uuid'

    def __init__(self, **kwargs):
        kwargs['default'] = uuid.uuid4().hex
        super(RandomSecretField, self).__init__(**kwargs)

    def db_value(self, value):
        return value

    def python_value(self, value):
        return value

