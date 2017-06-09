from typing import List, Dict, Any
import functools
import operator

from piper_driver.repository.repository import Repository
from piper_driver.models import *


class UsersRepository(Repository):

    @staticmethod
    def list(user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10, offset: int = 0) \
            -> List[Dict[Any, Any]]:
        pass

    @staticmethod
    def count(user: User, filters: Dict[str, Any] = None) -> int:
        pass

    @staticmethod
    def update(user: User, idx, values: Dict[str, Any]) -> None:
        pass

    @staticmethod
    def create(user: User, values: Dict[str, Any]) -> int:
        pass

    @staticmethod
    def delete(user: User, idx) -> None:
        pass
