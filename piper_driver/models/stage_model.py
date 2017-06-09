from enum import Enum

from peewee import PrimaryKeyField
from peewee import ForeignKeyField
from peewee import CharField
from peewee import IntegerField

from piper_driver.models.base_model import BaseModel, database_proxy
from piper_driver.models.fields import EnumField
from piper_driver.models.build_model import Build, BuildStatus


class StageStatus(Enum):
    CREATED = 1
    READY = 2
    PENDING = 3
    RUNNING = 4
    FAILED = 5
    SUCCESS = 6
    CANCELED = 7
    SKIPPED = 8
    ERROR = 9


class Stage(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    order = IntegerField()
    build = ForeignKeyField(Build, on_delete='CASCADE')
    status = EnumField(choices=StageStatus, default=StageStatus.CREATED)

    def save(self, force_insert=False, only=None, direct=True):
        from piper_driver.models.job_model import Job, JobStatus

        if Stage.status not in self.dirty_fields:
            return super().save(force_insert, only)

        old = self.build.status
        with database_proxy.transaction() as txn:
            try:
                if direct:
                    Job.update(status=JobStatus(self.status.value)).where(Job.stage == self).execute()
                statuses = {x.status for x in Stage.select(Stage.status).where((Stage.build == self.build) & (Stage.id != self.id))}
                statuses.add(self.status)

                severity = [
                    StageStatus.RUNNING,
                    StageStatus.PENDING,
                    StageStatus.CREATED,
                    StageStatus.READY,
                    StageStatus.ERROR,
                    StageStatus.FAILED,
                    StageStatus.CANCELED,
                    StageStatus.SKIPPED,
                ]

                for s in severity:
                    if s in statuses:
                        self.build.status = BuildStatus(s.value)

                self.build.save(direct=False)
                super().save(force_insert, only)
            except Exception as e:
                self.build.status = old
                txn.rollback()
                raise e

