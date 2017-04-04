from typing import Optional
from piper_driver.addins.common import Common


class ConnectionProxy:
    connection = None


queue_proxy = ConnectionProxy()


class Queue:

    def __init__(self, name: str):
        self.connection = queue_proxy.connection
        self._name = name

    def pop(self) -> Optional[str]:
        value = self.connection.lpop(Common.REDIS_PREFIX + ':queue:' + self.name)
        if value is None:
            return None

        return value.decode()

    def push(self, item: str) -> None:
        self.connection.rpush(Common.REDIS_PREFIX + ':queue:' + self.name, item)

    @property
    def name(self):
        return self._name
