import functools
import operator
from typing import List, Dict, Any

from jsonschema import Draft4Validator, ValidationError
from peewee import DoesNotExist

from piper_core.model.base_model import database_proxy
from piper_core.model.builds import *
from piper_core.model.projects import *
from piper_core.model.users import *

from piper_core.utils.exceptions import *
from piper_core.utils.github import Github


class BuildsFacade:

    def __init__(self, queue, schema, github: Github) -> None:
        self.queue = queue
        self.schema = schema
        self.github = github

    def get(self, user: User, idx: int) -> Dict[Any, Any]:
        try:
            build = Build.get(Build.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        result = {
            'id': build.id,
            'project_id': build.project.id,
            'status': build.status.to_str(),
            'branch': build.branch,
            'commit': build.commit,
        }

        return result

    def list(self, user: User, filters: Dict[str, Any] = None, order: List[str] = None,
             limit: int = 10, offset: int = 0) -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()

        _filters = list()

        if 'project_id' in filters:
            _filters.append((Build.project == filters['project_id']))
        if 'status' in filters:
            _filters.append((Build.status == Status.from_str(filters['status'])))
        if 'branch' in filters:
            _filters.append((Build.branch == filters['branch']))

        _order = list()
        for o in order:
            if o == 'created-desc':
                _order.append(Build.id.desc())
            if o == 'created-asc':
                _order.append(Build.id.asc())
        if len(_order) == 0:
            _order.append(Build.id.desc())

        query = Build.select(Build).distinct()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        query = query.order_by(*_order)

        result = list()
        for build in query:
            result.append({
                'id': build.id,
                'project_id': build.project.id,
                'status': build.status.to_str(),
                'branch': build.branch,
                'commit': build.commit,
            })

        return result

    def count(self, user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()

        _filters = list()

        if 'project_id' in filters:
            _filters.append((Build.project == filters['project_id']))
        if 'status' in filters:
            _filters.append((Build.status == Status.from_str(filters['status'])))
        if 'branch' in filters:
            _filters.append((Build.branch == filters['branch']))

        query = Build.select(Build).distinct()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.count()

    def cancel(self, user: User, idx: int) -> None:
        try:
            build: Build = Build.get(Build.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == build.project))
            except DoesNotExist:
                raise FacadeUnauthorized

        if build.status not in Status.cancelable_statuses():
            raise FacadeInvalidAction

        build.cancel()

    def restart(self, user: User, idx: int) -> None:
        from piper_core.model.jobs.job import Job
        from piper_core.model.stages.stage import Stage

        try:
            build: Build = Build.get(Build.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == build.project))
            except DoesNotExist:
                raise FacadeUnauthorized

        if build.status not in Status.final_statuses():
            raise FacadeInvalidAction

        build.restart()
        first = Stage.select().where(Stage.build == build).order_by(Stage.order.asc()).first()
        jobs = Job.select().where(Job.stage == first)
        for job in jobs:
            job.status = Status.READY
            job.save()
            self.queue.push(job)

    def create_build(self, yml: Dict[Any, Any], build: Build):
        from piper_core.model.stages.stage import Stage
        from piper_core.model.jobs.job import Job
        from piper_core.model.jobs.environment import Environment
        from piper_core.model.jobs.command import Command, CommandType

        hook_schema = self.schema['components']['schemas']['piper-yml']
        try:
            Draft4Validator(schema=hook_schema).validate(yml)
        except ValidationError as e:
            raise Exception(e.message)

        stages = dict()
        for idx, s in enumerate(yml['stages']):
            stage = Stage()
            stage.name = s
            stage.order = idx
            stage.build = build
            stages[s] = stage

        jobs = list()
        environments = list()
        commands = list()
        for job_name, job_def in yml['jobs'].items():
            if job_def['stage'] not in stages:
                raise Exception

            job = Job()
            job.stage = stages[job_def['stage']]
            jobs.append(job)

            if 'when' in job_def:
                job.only = job_def['when']

            if 'runner' in job_def:
                # FIXME check if group exists
                job.group = job_def['runner']

            job.image = job_def['image']

            if 'env' in job_def:
                for env_name, env_value in job_def['env'].items():
                    env = Environment()
                    env.name = env_name
                    env.value = env_value
                    env.job = job
                    environments.append(env)

            for idx, command_cmd in enumerate(job_def['commands']):
                command = Command()
                command.order = idx
                command.cmd = command_cmd
                command.job = job
                command.type = CommandType.NORMAL
                commands.append(command)

            if 'after_failure' in job_def:
                for idx, command_cmd in enumerate(job_def['after_failure']):
                    command = Command()
                    command.order = idx
                    command.cmd = command_cmd
                    command.job = job
                    command.type = CommandType.AFTER_FAILURE
                    commands.append(command)

        with database_proxy.atomic():
            build.save()
            for _, stage in stages.items():
                stage.save()

            for job in jobs:
                job.save()

            for env in environments:
                env.save()

            for command in commands:
                command.save()

    def parse_webhook(self, data):
        from piper_core.model.stages.stage import Stage
        from piper_core.model.jobs.job import Job
        from piper_core.model.jobs.environment import Environment

        commit = self.github.parse_webhook(data)
        yml = self.github.fetch_piper_yml(commit)

        project = Project.get(Project.origin == commit.branch.repository.origin)
        build = Build(project=project, branch=commit.branch.name, commit=commit.sha)
        self.create_build(yml, build)

        jobs = Job.select().join(Stage).where(Stage.build == build)
        for job in jobs:
            Environment.create(name='PIPER', value=True, job=job)
            Environment.create(name='PIPER_BRANCH', value=commit.branch.name, job=job)
            Environment.create(name='PIPER_COMMIT', value=commit.sha, job=job)
            Environment.create(name='PIPER_COMMIT_MESSAGE', value=commit.message, job=job)
            Environment.create(name='PIPER_JOB_ID', value=job.id, job=job)
            Environment.create(name='PIPER_BUILD_ID', value=build.id, job=job)
            Environment.create(name='PIPER_STAGE', value=job.stage.name, job=job)

        first = Stage.select().where(Stage.build == build).order_by(Stage.order.asc()).first()

        jobs = Job.select().where(Job.stage == first)
        for job in jobs:
            job.status = Status.READY
            job.save()
            self.queue.push(job)
