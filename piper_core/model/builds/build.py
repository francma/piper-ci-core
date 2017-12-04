import datetime
from typing import List, Union

from peewee import PrimaryKeyField, ForeignKeyField, FixedCharField, CharField, DateTimeField

from piper_core.model.status import Status
from piper_core.model.base_model import BaseModel, database_proxy
from piper_core.model.fields import EnumField
from piper_core.model.projects.project import Project, ProjectStatus


class Build(BaseModel):
    id = PrimaryKeyField()
    project: Project = ForeignKeyField(Project, on_delete='CASCADE')
    branch = CharField()
    commit = FixedCharField(max_length=40)
    status: Status = EnumField(choices=Status, default=Status.CREATED)
    created = DateTimeField(default=datetime.datetime.now)

    @classmethod
    def create(cls, **query) -> 'Build':
        return super().create(**query)

    def cancel(self):
        from piper_core.model.stages.stage import Stage

        with database_proxy.transaction():
            stages: List[Stage] = Stage.select().where(Stage.build == self)
            for stage in stages:
                stage.cancel()

            self.status = Build.get(Build.id == self.id).status
            self._set_project_status()
            self.project.save()

    def restart(self):
        from piper_core.model.stages.stage import Stage

        with database_proxy.transaction():
            stages: List[Stage] = Stage.select().where(Stage.build == self)
            for stage in stages:
                stage.restart()

            stages: List[Stage] = Stage.select().where(Stage.build == self).order_by(Stage.order.asc()).offset(1)
            for stage in stages:
                stage.status = Status.PENDING
                stage.save()

            self.status = Build.get(Build.id == self.id).status
            self._set_project_status()
            self.project.save()

    def save(self, force_insert=False, only=None):
        if Build.status not in self.dirty_fields:
            return super(Build, self).save(force_insert, only)

        with database_proxy.transaction():
            self._set_project_status()
            self.project.save()

            return super(Build, self).save(force_insert, only)

    def _set_project_status(self):
        statuses = {x.status for x in Build.select(Build.status).where(
            (Build.project == self.project) & (Build.id != self.id)
        )}
        statuses.add(self.status)

        if statuses & {Status.ERROR}:
            self.project.status = ProjectStatus.ERROR
        elif statuses & {Status.FAILED}:
            self.project.status = ProjectStatus.FAILED
        elif statuses & {Status.RUNNING, Status.READY, Status.CREATED, Status.PENDING}:
            self.project.status = ProjectStatus.RUNNING
        elif statuses & {Status.SUCCESS}:
            self.project.status = ProjectStatus.SUCCESS
        elif statuses & {Status.CANCELED}:
            self.project.status = ProjectStatus.CANCELED
        elif statuses & {Status.SKIPPED}:
            self.project.status = ProjectStatus.SKIPPED
        elif statuses & {Status.CREATED}:
            self.project.status = ProjectStatus.UNKNOWN
