from typing import List
import functools
import operator

from peewee import DoesNotExist

from piper_driver.repository.repository import Repository
from piper_driver.models import *
from piper_driver.addins.exceptions import *


class BuildRepository(Repository):

    @staticmethod
    def get(idx: int, user: User) -> Dict[Any, Any]:
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
            'status': build.status,
        }

        return result

    @staticmethod
    def list(filters: Dict[str, Any], order: List[str], limit: int, offset: int, user: User) -> List[Dict[Any, Any]]:
        _filters = list()
        if user.role is not UserRole.MASTER:
            _filters.append((ProjectUser.user == user))
        else:
            if 'user_id' in filters:
                _filters.append((ProjectUser.user == filters['user_id']))

        if 'project_id' in filters:
            _filters.append((Project.id == filters['project_id']))
        if 'status' in filters:
            _filters.append((Build.status == BuildStatus.from_str(filters['status'])))
        if 'created' in filters:
            _filters.append((Build.created == filters['created']))
        if 'min-created' in filters:
            _filters.append((Build.created >= filters['min-created']))
        if 'max-created' in filters:
            _filters.append((Build.created >= filters['max-created']))
        if 'ref' in filters:
            _filters.append((Build.created == filters['ref']))

        _order = list()
        for o in order:
            if o == 'created-desc':
                _order.append(Build.id.desc())
            if o == 'created-asc':
                _order.append(Build.id.asc())
        if len(_order) == 0:
            _order.append(Build.id.desc())

        result = list()
        query = Build.select(Build).distinct()
        query = query.join(Project)
        query = query.join(ProjectUser)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.order_by(*_order)

        for build in query:
            result.append({
                'id': build.id,
                'project_id': build.project.id,
                'status': build.status,
            })

        return result

    @staticmethod
    def count(filters: Dict[str, Any], user: User, master: bool) -> int:
        _filters = list()
        if user.role is not UserRole.MASTER or not master:
            _filters.append((ProjectUser.user == user))

        if 'project_id' in filters:
            _filters.append((Project.id == filters['project_id']))
        if 'status' in filters:
            _filters.append((Build.status == BuildStatus.from_str(filters['status'])))
        if 'created' in filters:
            _filters.append((Build.created == filters['created']))
        if 'min-created' in filters:
            _filters.append((Build.created >= filters['min-created']))
        if 'max-created' in filters:
            _filters.append((Build.created >= filters['max-created']))
        if 'ref' in filters:
            _filters.append((Build.created == filters['ref']))

        query = Build.select(Build).distinct()
        query = query.join(Project)
        if user.role is not UserRole.MASTER or not master:
            query = query.join(ProjectUser)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.wrapped_count()

    @staticmethod
    def delete(idx: int, user: User) -> None:
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
