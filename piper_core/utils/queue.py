from typing import Optional

from redis import Redis


class Queue:

    def __init__(self, connection: Redis) -> None:
        self.connection = connection

    def pop(self, queue: str) -> Optional[str]:
        value = self.connection.lpop('queue:' + queue)
        if value is None:
            return None

        return value.decode()

    def push(self, queue: str, item: str) -> None:
        self.connection.rpush('queue:' + queue, item)
