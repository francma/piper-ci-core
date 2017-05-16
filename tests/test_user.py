import pytest

from piper_driver.models import *


def test_model():
    user = User()
    with pytest.raises(ModelInvalid):
        user.email = 'invalid email'
    with pytest.raises(ModelInvalid):
        user.email = list()
    user.email = 'me@martinfranc.eu'

    with pytest.raises(ModelInvalid):
        user.role = 'invalid'
    with pytest.raises(ModelInvalid):
        user.role = list()
    user.role = UserRole.MASTER
