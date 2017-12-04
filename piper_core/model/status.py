from enum import Enum


class Status(Enum):
    CREATED = 1
    READY = 2
    PENDING = 3
    RUNNING = 4
    FAILED = 5
    SUCCESS = 6
    CANCELED = 7
    SKIPPED = 8
    ERROR = 9

    @classmethod
    def final_statuses(cls):
        return [
            cls.FAILED,
            cls.SUCCESS,
            cls.CANCELED,
            cls.ERROR,
            cls.SKIPPED,
        ]

    @classmethod
    def cancelable_statuses(cls):
        return [
            cls.CREATED,
            cls.READY,
            cls.PENDING,
            cls.RUNNING,
        ]

    def __str__(self):
        return self.name.lower()

    def to_str(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, string: str):
        return cls.__getattr__(string.upper())  # type: ignore
