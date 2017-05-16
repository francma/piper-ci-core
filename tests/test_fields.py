from piper_driver.models import *
from piper_driver.models.fields import RandomSecretField


def test_secret(connection):
    class TestModel(BaseModel):
        secret = RandomSecretField()

    connection.create_tables([TestModel])

    test = TestModel()
    assert len(test.secret) != 0
    test.save()
    assert len(test.secret) != 0

