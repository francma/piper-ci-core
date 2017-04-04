import pytest

from piper_driver.models import *


def test_model():
    user = User()
    with pytest.raises(ModelInvalidValueException):
        user.email = 'invalid email'
    with pytest.raises(ModelInvalidValueException):
        user.email = list()
    user.email = 'me@martinfranc.eu'

    with pytest.raises(ModelInvalidValueException):
        user.role = 'invalid'
    with pytest.raises(ModelInvalidValueException):
        user.role = list()
    user.role = UserRole.ROOT
