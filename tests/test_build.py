import pytest

from piper_driver.models import *


def test_model():
    build = Build()
    with pytest.raises(ModelInvalidValueException):
        build.commit = 'invalid'
    with pytest.raises(ModelInvalidValueException):
        build.commit = list()
    with pytest.raises(ModelInvalidValueException):
        build.status = 'invalid'
    with pytest.raises(ModelInvalidValueException):
        build.status = list()
    with pytest.raises(ModelInvalidValueException):
        build.ref = 1
    with pytest.raises(ModelInvalidValueException):
        build.ref = list()
    build.commit = '634721d9da222050d41dce164d9de35fe475aa7a'
    build.status = BuildStatus.NEW
    build.ref = 'master'
