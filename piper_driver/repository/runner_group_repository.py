from piper_driver.repository.repository import Repository
from piper_driver.models import *


class RunnerGroupRepository(Repository):

    def get(self, idx, user: User):
        pass

    def update(self, idx, values: Dict[str, Any], user: User):
        pass

    def create(self, idx, values: Dict[str, Any], user: User):
        pass

    def list(self, filters: Dict[str, Any], limit: int, offset: int, user: User):
        pass

    def delete(self, idx, user):
        pass
