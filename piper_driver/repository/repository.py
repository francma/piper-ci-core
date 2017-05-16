from typing import Any
from typing import Dict
from typing import List

from piper_driver.addins.exceptions import PiperException
from piper_driver.models import User


class RepositoryException(PiperException):
    pass


class RepositoryNotImplementedException(RepositoryException):
    pass


class Repository:

    @staticmethod
    def get(idx, user: User) -> Dict[Any, Any]:
        raise RepositoryNotImplementedException

    @staticmethod
    def count(filters: Dict[str, Any], user: User, master: bool) -> int:
        raise RepositoryNotImplementedException

    @staticmethod
    def list(filters: Dict[str, Any], order: List[str], limit: int, offset: int, user: User) -> List[Dict[Any, Any]]:
        raise RepositoryNotImplementedException

    @staticmethod
    def update(idx, values: Dict[str, Any], user: User) -> None:
        raise RepositoryNotImplementedException

    @staticmethod
    def create(values: Dict[str, Any], user: User) -> int:
        raise RepositoryNotImplementedException

    @staticmethod
    def delete(idx, user) -> None:
        raise RepositoryNotImplementedException
