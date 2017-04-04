from peewee import PrimaryKeyField
from peewee import ForeignKeyField

from piper_driver.models.base_model import BaseModel
from piper_driver.models.fields import RandomSecretField
from piper_driver.models.project_model import Project
from piper_driver.models.runner_group_model import RunnerGroup


class Runner(BaseModel):
    id = PrimaryKeyField()
    group = ForeignKeyField(RunnerGroup, null=True)
    token = RandomSecretField()


class ProjectRunner(BaseModel):
    project = ForeignKeyField(Project)
    runner = ForeignKeyField(Runner)
