from typing import Any, Dict, List

from piper_driver.addins.exceptions import PiperException
from piper_driver.models import User


class RepositoryException(PiperException):
    pass


class RepositoryNotImplementedException(RepositoryException):
    pass


class Repository:

    @staticmethod
    def get(user: User, idx) -> Dict[Any, Any]:
        raise RepositoryNotImplementedException

    @staticmethod
    def list(user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10, offset: int = 0)\
            -> List[Dict[Any, Any]]:
        raise RepositoryNotImplementedException

    @staticmethod
    def count(user: User, filters: Dict[str, Any] = None) -> int:
        raise RepositoryNotImplementedException

    @staticmethod
    def update(user: User, idx, values: Dict[str, Any]) -> None:
        raise RepositoryNotImplementedException

    @staticmethod
    def create(user: User, values: Dict[str, Any]) -> int:
        raise RepositoryNotImplementedException

    @staticmethod
    def delete(user: User, idx) -> None:
        raise RepositoryNotImplementedException
