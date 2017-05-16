from typing import Dict, Any, Optional
import random

import yaml
from simpleeval import simple_eval, InvalidExpression
from peewee import PeeweeException

from piper_driver.addins.queue import Queue
from piper_driver.addins.exceptions import *
from piper_driver.models.base_model import BaseModel
from piper_driver.models.base_model import database_proxy
from piper_driver.models.user_model import User, UserRole
from piper_driver.models.project_model import Project, ProjectUser, ProjectRole
from piper_driver.models.runner_model import Runner, ProjectRunner
from piper_driver.models.runner_group_model import RunnerGroup
from piper_driver.models.build_model import Build, BuildStatus
from piper_driver.models.stage_model import Stage, StageStatus
from piper_driver.models.job_model import Job, JobStatus, JobError
from piper_driver.models.command_model import Command
from piper_driver.models.environment_model import Environment


models = [
    Project,
    Runner,
    Build,
    Job,
    User,
    ProjectRunner,
    Stage,
    ProjectUser,
    Environment,
    Command,
    RunnerGroup,
]


def load_config(build: Build, yml: str) -> None:
    d = yaml.safe_load(yml)
    if type(d) is not dict:
        raise Exception
    if 'stages' not in d:
        raise Exception
    if type(d['stages']) is not list:
        raise Exception
    stages = dict()
    for idx, s in enumerate(d['stages']):
        stage = Stage()
        stage.name = s
        stage.order = idx
        stage.build = build
        stages[s] = stage

    if 'jobs' not in d:
        raise Exception
    if type(d['jobs']) is not dict:
        raise Exception

    jobs = list()
    environments = list()
    commands = list()
    for job_name, job_def in d['jobs'].items():
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
            job.only = job_def['only']

        if 'runner' in job_def:
            if type(job_def['runner']) is not str:
                raise Exception
            group = RunnerGroup.get(RunnerGroup.name == job_def['runner'])
            # FIXME check if group exists
            job.group = group

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
            build.save()
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


def job_env2dict(job: Job) -> Dict[Any, Any]:
    names = dict()
    for env in Environment.select().where(Environment.job == job):
        names[env.name] = env.value

    return names


def job_runner_export(job: Job) -> Dict[Any, Any]:
    """
    {
        "commands": ["first", "second"],
        "after_failure": ["first", "second"], # OPTIONAL
        "env": {"name1": "value1", "name2": "value2"}, # OPTIONAL
        "image": "image name",
        "repository": {
            "origin": "git@git.git",
            "branch": "branch",
            "commit": "634721d9da222050d41dce164d9de35fe475aa7a"
            "pubkeys": [ # OPTIONAL (only private repos needs this)
                "sha ...",
                "sha ..."
            ]
        }
    }
    """
    result = {
        'commands': [],
    }
    commands = Command.select().where(Command.job == job).order_by(Command.order.asc())
    for command in commands:
        result['commands'].append(command.cmd)

    env = job_env2dict(job)
    if env:
        result['env'] = env

    result['image'] = job.image

    build = job.stage.build
    project = build.project
    result['repository'] = {
        'origin': project.origin,
        'branch': build.ref,
        'commit': build.commit,
    }

    return result


def job_evaluate_condition(job: Job) -> bool:
    names = job_env2dict(job)

    try:
        return bool(simple_eval(job.only, names=names))
    except (InvalidExpression, SyntaxError) as e:
        raise JobOnlyExpressionException(str(e))


def job_queue_pop(runner: Runner) -> Optional[Job]:
    """
    1) Runner has RunnerGroup assigned
    Runner will take job with same group or with no group (RunnerGroup.NONE_GROUP).
    Jobs are selected only from Runner's projects.
    
    2) Runner do not have RunnerGroup
    Runner will take job from all groups, including RunnerGroup.NONE_GROUP.
    Jobs are selected only from Runner's projects.
    """
    projects = Project.select().join(ProjectRunner).where(ProjectRunner.runner == runner)
    projects = list(projects)

    if runner.group is None:
        groups = list(RunnerGroup.select()) + [RunnerGroup.NONE_GROUP]
    else:
        groups = [runner.group, RunnerGroup.NONE_GROUP]

    random.shuffle(projects)
    random.shuffle(groups)

    item = None
    for project in projects:
        for group in groups:
            queue = '{}:{}'.format(project.id, group.name)
            item = Queue.pop(queue)
            if item is not None:
                break
        else:
            # for loop ended without break
            continue
        break

    if item is None:
        return None

    job = Job.get(Job.id == int(item))

    return job


def job_queue_push(job: Job) -> None:
    """
    Queue name: "`Queue.QUEUE_PREFIX`:<project.id>:<group.name>"
    If job has no group, it will be assigned to RunnerGroup.NONE_GROUP
    """
    group = job.group if job.group else RunnerGroup.NONE_GROUP
    queue = '{}:{}'.format(job.stage.build.project.id, group.name)
    Queue.push(queue, str(job.id))


def build_save(self, force_insert=False, only=None, direct=True):
    if Build.status not in self.dirty_fields:
        super(Build, self).save(force_insert, only)
        return

    super(Build, self).save(force_insert, only)


def stage_save(self, force_insert=False, only=None, direct=True):
    if Stage.status not in self.dirty_fields:
        super(Stage, self).save(force_insert, only)
        return

    with database_proxy.transaction() as txn:
        try:
            if direct and self.status is StageStatus.CANCELED:
                cancelable = [JobStatus.RUNNING, JobStatus.READY, JobStatus.CREATED]
                Job.update(status=JobStatus.CANCELED).where((Job.stage == self) & (Job.status << cancelable)).execute()
            build = self.build
            old_build_status = build.status
            statuses = {x.status for x in Stage.select(Stage.status).where((Stage.build == build) & (Stage.id != self.id))}
            statuses.add(self.status)

            if statuses == set([StageStatus.CREATED]):
                build.status = BuildStatus.CREATED
            elif statuses == set([StageStatus.PENDING]):
                build.status = BuildStatus.PENDING
            elif StageStatus.RUNNING in statuses:
                build.status = BuildStatus.RUNNING
            elif StageStatus.FAILED in statuses and len(set([StageStatus.RUNNING, StageStatus.CREATED, StageStatus.PENDING]) & statuses) == 0:
                build.status = BuildStatus.FAILED
            elif statuses == set([StageStatus.SUCCESS]):
                build.status = BuildStatus.SUCCESS
            elif statuses == set([StageStatus.SUCCESS, StageStatus.CANCELED]):
                build.status = BuildStatus.CANCELED

            build.save(direct=False)
            super(Stage, self).save(force_insert, only)
        except Exception as e:
            build.status = old_build_status
            txn.rollback()
            raise e


def job_save(self, force_insert=False, only=None):
    if Job.status not in self.dirty_fields:
        super(Job, self).save(force_insert, only)
        return

    with database_proxy.transaction() as txn:
        try:
            stage = self.stage
            old_stage_status = stage.status
            statuses = {x.status for x in Job.select(Job.status).where((Job.stage == stage) & (Job.id != self.id))}
            statuses.add(self.status)

            # Build > Stage > Job
            if statuses == set([JobStatus.CREATED]):
                stage.status = StageStatus.CREATED
            elif statuses == set([JobStatus.PENDING, JobStatus.READY]):
                stage.status = StageStatus.PENDING
            elif JobStatus.RUNNING in statuses:
                stage.status = StageStatus.RUNNING
            elif statuses in [set(x) for x in [[JobStatus.FAILED], [JobStatus.FAILED, JobStatus.CANCELED], [JobStatus.FAILED, JobStatus.SUCCESS], [JobStatus.FAILED, JobStatus.CANCELED, JobStatus.SUCCESS]]]:
                stage.status = StageStatus.FAILED
            elif statuses == set([JobStatus.SUCCESS]):
                stage.status = StageStatus.SUCCESS
            elif statuses in [set(x) for x in [[JobStatus.SUCCESS, JobStatus.CANCELED], [JobStatus.CANCELED]]]:
                stage.status = StageStatus.CANCELED

            stage.save(direct=False)
            super(Job, self).save(force_insert, only)
        except Exception as e:
            stage.status = old_stage_status
            txn.rollback()
            raise e


Stage.save = stage_save
Job.save = job_save
Build.save = build_save


