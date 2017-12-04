from peewee import Field


class EnumField(Field):
    db_field = 'int'

    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return self.choices(value)
