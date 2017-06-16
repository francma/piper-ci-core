import functools
import operator
from typing import List, Dict, Any

from piper_driver.repository.repository import Repository
from piper_driver.models import *
from piper_driver.addins.exceptions import *

from peewee import DoesNotExist


class JobRepository(Repository):

    @staticmethod
    def get(user: User, idx: int) -> Dict[Any, Any]:
        try:
            job = Job.get(Job.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == job.stage.project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied

        commands = Command.select().where(Command.job == job).order_by(Command.order.desc())
        _commands = list()
        for command in commands:
            _commands.append(command.cmd)

        result = {
            'id': job.id,
            'stage_id': job.stage.id,
            'status': job.status.to_str(),
            'group': job.group,
            'image': job.image,
            'when': job.when,
            'commands': job.commands,
            'env': job.environment,
        }

        return result

    @staticmethod
    def list(user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10, offset: int = 0)\
            -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()

        _filters = list()
        if user.role is not UserRole.MASTER:
            _filters.append((ProjectUser.user == user))
        else:
            if 'user_id' in filters:
                _filters.append((ProjectUser.user == filters['user_id']))

        if 'project_id' in filters:
            _filters.append((Project.id == filters['project_id']))
        if 'status' in filters:
            _filters.append((Job.status == JobStatus.from_str(filters['status'])))
        if 'build_id' in filters:
            _filters.append((Build.id == filters['build_id']))

        _order = list()
        for o in order:
            if o == 'created-desc':
                _order.append(Job.id.desc())
            if o == 'created-asc':
                _order.append(Job.id.asc())
        if len(_order) == 0:
            _order.append(Job.id.desc())

        result = list()
        query = Job.select(Job).distinct().join(Stage).join(Build).join(Project)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.order_by(*_order)

        for job in query:
            result.append({
                'id': job.id,
                'stage_id': job.stage.id,
                'status': job.status.to_str(),
                'group': job.group,
                'image': job.image,
                'when': job.when,
            })

        return result

    @staticmethod
    def cancel(idx, user: User) -> None:
        try:
            job = Job.get(Job.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                project_role = ProjectUser.get((ProjectUser.user == user) &
                                               (ProjectUser.project == job.stage.build.project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied

            if project_role not in [ProjectRole.MASTER, ProjectRole.DEVELOPER]:
                raise RepositoryPermissionDenied

        job.status = JobStatus.CANCELED
        job.save()

    @staticmethod
    def read_log(user: User, idx, offset: int=0, limit: int=100):
        try:
            job = Job.get(Job.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == job.stage.build.project))
            except DoesNotExist:
                raise RepositoryPermissionDenied

        data = job.read_log(offset, limit)

        return data

    @staticmethod
    def append_log(job: Job, contents):
        job.append_log(contents)

