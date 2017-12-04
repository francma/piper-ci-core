import uuid
from peewee import CharField
from peewee import ForeignKeyField
from peewee import IntegerField, DoesNotExist
from peewee import PrimaryKeyField
from typing import Union

from piper_core.model.base_model import BaseModel, database_proxy
from piper_core.model.builds.build import Build, Status
from piper_core.model.fields import EnumField


class Stage(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    order = IntegerField()
    build: Build = ForeignKeyField(Build, on_delete='CASCADE')
    status: Status = EnumField(choices=Status, default=Status.CREATED)

    @classmethod
    def create(cls, **query) -> 'Stage':
        return super().create(**query)

    def cancel(self):
        from piper_core.model.jobs.job import Job

        with database_proxy.transaction():
            jobs = Job.select().where(
                (Job.stage == self) & (Job.status.in_(Status.cancelable_statuses()))
            )
            for job in jobs:
                job.status = Status.CANCELED
                job.save()

            self.status = Stage.get(Stage.id == self.id).status
            self._set_build_status()
            self.build.save()

    def restart(self):
        from piper_core.model.jobs.job import Job

        with database_proxy.transaction():
            jobs = Job.select().where(
                (Job.stage == self) & (Job.status.in_(Status.final_statuses()))
            )

            for job in jobs:
                job.status = Status.READY
                job.secret = uuid.uuid4().hex
                job.save()

            self.status = Stage.get(Stage.id == self.id).status
            self._set_build_status()
            self.build.save()

    def save(self, force_insert=False, only=None):
        from piper_core.model.jobs.job import Job

        if Stage.status not in self.dirty_fields:
            return super().save(force_insert, only)

        with database_proxy.transaction():
            if self.status is Status.RUNNING:
                stages = Stage.select().where(
                    (Stage.order > self.order) &
                    (Stage.build == self.build) &
                    Stage.status.not_in(Status.final_statuses())
                )
                for stage in stages:
                    stage.status = Status.PENDING
                    Job.update(status=Status.PENDING).where(Job.stage == stage).execute()
                    stage.save()

            if self.status in [Status.CANCELED, Status.SKIPPED, Status.SUCCESS]:
                try:
                    stage = Stage.get(
                        (Stage.order == self.order + 1) &
                        (Stage.build == self.build) &
                        Stage.status.not_in(Status.final_statuses())
                    )
                    stage.status = Status.READY
                    Job.update(status=Status.READY).where(Job.stage == stage).execute()
                    stage.save()
                except DoesNotExist:
                    pass

            if self.status in [Status.FAILED, Status.ERROR]:
                stages = Stage.select().where(
                    (Stage.order > self.order) &
                    (Stage.build == self.build) &
                    Stage.status.not_in(Status.final_statuses())
                )
                for stage in stages:
                    Job.update(status=Status.FAILED).where(Job.stage == stage).execute()
                    stage.status = Status.FAILED
                    stage.save()

            self._set_build_status()
            self.build.save()
            return super().save(force_insert, only)

    def _set_build_status(self):
        statuses = {x.status for x in Stage.select(Stage.status).where(
            (Stage.build == self.build) & (Stage.id != self.id)
        )}
        statuses.add(self.status)

        if statuses & {Status.ERROR}:
            self.build.status = Status.ERROR
        elif statuses & {Status.FAILED}:
            self.build.status = Status.FAILED
        elif statuses & {Status.RUNNING}:
            self.build.status = Status.RUNNING
        elif statuses & {Status.READY}:
            if statuses & {Status.SUCCESS, Status.CANCELED, Status.SKIPPED}:
                self.build.status = Status.RUNNING
            else:
                self.build.status = Status.READY
        elif statuses & {Status.SUCCESS}:
            self.build.status = Status.SUCCESS
        elif statuses & {Status.CANCELED}:
            self.build.status = Status.CANCELED
        elif statuses & {Status.SKIPPED}:
            self.build.status = Status.SKIPPED
        elif statuses & {Status.CREATED}:
            self.build.status = Status.CREATED
