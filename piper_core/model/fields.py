from peewee import Field, BlobField
import pickle


class EnumField(Field):
    db_field = 'int'

    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return self.choices(value)


class PickledField(BlobField):
    def db_value(self, value):
        if value is not None:
            return pickle.dumps(value)

    def python_value(self, value):
        if value is not None:
            if isinstance(value, str):
                value = value.encode('raw_unicode_escape')
            return pickle.loads(value)
