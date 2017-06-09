from enum import Enum
import re
import datetime
from typing import Dict, Any

from peewee import PeeweeException, PrimaryKeyField, ForeignKeyField, FixedCharField, CharField, DateTimeField

from piper_driver.addins.exceptions import *
from piper_driver.models.base_model import BaseModel, database_proxy
from piper_driver.models.fields import EnumField
from piper_driver.models.project_model import Project


class BuildStatus(Enum):
    CREATED = 1
    READY = 2
    PENDING = 3
    RUNNING = 4
    FAILED = 5
    SUCCESS = 6
    CANCELED = 7
    SKIPPED = 8
    ERROR = 9

    def to_str(self):
        return self.name.lower()

    @staticmethod
    def from_str(string: str):
        return BuildStatus.__getattr__(string.upper())


class Build(BaseModel):
    id = PrimaryKeyField()
    project = ForeignKeyField(Project, on_delete='CASCADE')
    branch = CharField()
    commit = FixedCharField(max_length=40)
    status = EnumField(choices=BuildStatus, default=BuildStatus.CREATED)
    created = DateTimeField(default=datetime.datetime.now)

    def save(self, force_insert=False, only=None, direct=True):
        from piper_driver.models.stage_model import Stage, StageStatus
        from piper_driver.models.job_model import Job, JobStatus

        errors = list()
        if not self.validate(errors):
            raise ModelInvalid(errors)

        if Build.status not in self.dirty_fields:
            return super(Build, self).save(force_insert, only)

        with database_proxy.transaction() as txn:
            try:
                stages = Stage.select(Stage.id).where(Stage.build == self).scalar(as_tuple=True)
                if stages:
                    Job.update(status=JobStatus(self.status.value)).where(Job.stage << stages).execute()
                    Stage.update(status=StageStatus(self.status.value)).where(Stage.id << stages).execute()
                return super(Build, self).save(force_insert, only)
            except Exception as e:
                txn.rollback()
                raise e

    def load_config(self, yml: Dict[Any, Any]) -> None:
        from piper_driver.models.stage_model import Stage
        from piper_driver.models.job_model import Job
        from piper_driver.models.environment_model import Environment
        from piper_driver.models.command_model import Command

        if 'stages' not in yml:
            raise Exception
        if type(yml['stages']) is not list:
            raise Exception
        stages = dict()
        for idx, s in enumerate(yml['stages']):
            stage = Stage()
            stage.name = s
            stage.order = idx
            stage.build = self
            stages[s] = stage

        if 'jobs' not in yml:
            raise Exception
        if type(yml['jobs']) is not dict:
            raise Exception

        jobs = list()
        environments = list()
        commands = list()
        for job_name, job_def in yml['jobs'].items():
            if type(job_def) is not dict:
                raise Exception
            if 'stage' not in job_def:
                raise Exception
            if 'commands' not in job_def:
                raise Exception
            if job_def['stage'] not in stages:
                raise Exception

            job = Job()
            job.stage = stages[job_def['stage']]
            jobs.append(job)

            if 'only' in job_def:
                job.when = job_def['only']

            if 'runner' in job_def:
                if type(job_def['runner']) is not str:
                    raise Exception
                # FIXME check if group exists
                job.group = job_def['runner']

            if 'image' in job_def:
                job.image = job_def['image']

            if 'env' in job_def:
                if type(job_def['env']) is not dict:
                    raise Exception
                for env_name, env_value in job_def['env'].items():
                    env = Environment()
                    env.name = env_name
                    env.value = env_value
                    env.job = job
                    environments.append(env)

            if not isinstance(job_def['commands'], list):
                raise Exception

            for idx, command_cmd in enumerate(job_def['commands']):
                command = Command()
                command.order = idx
                command.cmd = command_cmd
                command.job = job
                commands.append(command)

        with database_proxy.atomic() as transaction:
            try:
                self.save()
                for _, stage in stages.items():
                    stage.save()

                for job in jobs:
                    job.save()

                for env in environments:
                    env.save()

                for command in commands:
                    command.save()
            except PeeweeException as e:
                transaction.rollback()
                raise e

    def validate(self, errors=None):
        if errors is None:
            errors = list()

        if not isinstance(self.status, BuildStatus):
            errors.append('build')
        if not isinstance(self.commit, str) or not re.match(r'^[a-f0-9]{40}$', self.commit):
            errors.append('commit')
        if not isinstance(self.branch, str):
            errors.append('branch')

        return len(errors) == 0
