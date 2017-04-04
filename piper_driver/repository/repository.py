from typing import Any
from typing import Dict
from typing import List

from piper_driver.addins.exceptions import PiperException
from piper_driver.models.entities import User


class RepositoryException(PiperException):
    pass


class RepositoryNotImplementedException(RepositoryException):
    pass


class Repository:

    def get(self, idx, properties: List[str], user: User):
        raise RepositoryNotImplementedException

    def update(self, idx, properties: Dict[str, Any], user: User):
        raise RepositoryNotImplementedException

    def create(self, idx, properties: Dict[str, Any], user: User):
        raise RepositoryNotImplementedException

    def list(self, user: User, properties: List[str]):
        raise RepositoryNotImplementedException
