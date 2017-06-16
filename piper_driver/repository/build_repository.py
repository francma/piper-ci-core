import functools
import operator
from typing import List, Dict, Any

from peewee import DoesNotExist

from piper_driver.repository.repository import Repository
from piper_driver.models import *
from piper_driver.addins.exceptions import *


class BuildsRepository(Repository):

    @staticmethod
    def get(user: User, idx: int) -> Dict[Any, Any]:
        try:
            build = Build.get(Build.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == build.project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied

        result = {
            'id': build.id,
            'project_id': build.project.id,
            'status': build.status.to_str(),
            'branch': build.branch,
            'commit': build.commit,
        }

        return result

    @staticmethod
    def list(user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10, offset: int = 0) \
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
            _filters.append((Build.project == filters['project_id']))
        if 'status' in filters:
            _filters.append((Build.status == BuildStatus.from_str(filters['status'])))
        if 'created' in filters:
            _filters.append((Build.created == filters['created']))
        if 'min-created' in filters:
            _filters.append((Build.created >= filters['min-created']))
        if 'max-created' in filters:
            _filters.append((Build.created <= filters['max-created']))
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
        if ('user_id' in filters and user.role is UserRole.MASTER) or user.role is not UserRole.MASTER:
            query = query.join(ProjectUser, on=(Build.project == ProjectUser.project))
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.limit(offset)
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

    @staticmethod
    def count(user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()

        _filters = list()
        if user.role is not UserRole.MASTER:
            _filters.append((ProjectUser.user == user))
        else:
            if 'user_id' in filters:
                _filters.append((ProjectUser.user == filters['user_id']))

        if 'project_id' in filters:
            _filters.append((Build.project == filters['project_id']))
        if 'status' in filters:
            _filters.append((Build.status == BuildStatus.from_str(filters['status'])))
        if 'created' in filters:
            _filters.append((Build.created == filters['created']))
        if 'min-created' in filters:
            _filters.append((Build.created >= filters['min-created']))
        if 'max-created' in filters:
            _filters.append((Build.created <= filters['max-created']))
        if 'branch' in filters:
            _filters.append((Build.branch == filters['branch']))

        query = Build.select(Build).distinct()
        if ('user_id' in filters and user.role is UserRole.MASTER) or user.role is not UserRole.MASTER:
            query = query.join(ProjectUser, on=(Build.project == ProjectUser.project))
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.wrapped_count()

    @staticmethod
    def cancel(user: User, idx: int) -> None:
        try:
            build = Build.get(Build.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is UserRole.MASTER:
            build.status = BuildStatus.CANCELED
            build.save()
            return

        try:
            project_role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == build.project)).role
        except DoesNotExist:
            raise RepositoryPermissionDenied

        if project_role not in [ProjectRole.MASTER, ProjectRole.DEVELOPER]:
            raise RepositoryPermissionDenied

        build.status = BuildStatus.CANCELED
        build.save()
