from typing import List
from typing import Dict
from typing import Any

from piper_driver.models.entities import User
from piper_driver.models.entities import UserRole
from piper_driver.repository.repository import *


class IdentityRepository(Repository):

    def get(self, user: User, properties=None):
        if properties is None:
            properties = ['id', 'username', 'email', 'role']

        result = {x: getattr(user, x) for x in properties}

        return result

    def update(self, properties: Dict[str, Any], user: User):
        if 'role' in properties and user.role is not UserRole.ROOT:
            return False

        for k, v in properties.items():
            setattr(user, k, v)
        user.save()

        return True

    def create(self, idx, properties: Dict[str, Any], user: User):
        raise RepositoryNotImplementedException

    def list(self, user: User, properties: List[str]):
        raise RepositoryNotImplementedException

