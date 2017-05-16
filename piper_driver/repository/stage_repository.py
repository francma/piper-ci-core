from piper_driver.repository.repository import Repository
from piper_driver.models import *


class StageRepository(Repository):

    def get(self, idx, user: User):
        pass

    def list(self, filters: Dict[str, Any], limit: int, offset: int, user: User):
        pass

    def delete(self, filters: Dict[str, Any], limit: int, offset: int, user: User):
        pass
