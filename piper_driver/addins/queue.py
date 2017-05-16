from typing import Optional
from piper_driver.addins.common import Common


class Queue:

    connection = None

    @staticmethod
    def pop(queue: str) -> Optional[str]:
        value = Queue.connection.lpop(Common.REDIS_PREFIX + ':queue:' + queue)
        if value is None:
            return None

        return value.decode()

    @staticmethod
    def push(queue: str, item: str) -> None:
        Queue.connection.rpush(Common.REDIS_PREFIX + ':queue:' + queue, item)
