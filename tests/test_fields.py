import pytest
from peewee import PrimaryKeyField

from piper_driver.models import *
from piper_driver.models.fields import RandomSecretField


def test_secret(connection):
    class TestModel(BaseModel):
        id = PrimaryKeyField()
        _secret = RandomSecretField()

        @property
        def secret(self):
            return self._secret

        @secret.setter
        def secret(self, value):
            raise Exception

    connection.create_tables([TestModel])

    test = TestModel()
    with pytest.raises(Exception):
        test.secret = 'TEST'
    assert len(test.secret) != 0
    test.save()
    assert len(test.secret) != 0

