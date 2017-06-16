from typing import List, Dict, Any
import functools
import operator

from peewee import DoesNotExist

from piper_driver.repository.repository import Repository
from piper_driver.models import *
from piper_driver.addins.exceptions import *


class StagesRepository(Repository):

    @staticmethod
    def get(user: User, idx) -> Dict[Any, Any]:
        try:
            stage = Stage.get(Stage.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == stage.build.project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied

        result = {
            'id': stage.id,
            'build': stage.build.id,
            'status': stage.status.to_str(),
            'name': stage.name,
            'order': stage.order,
        }

        return result

    @staticmethod
    def list(user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10, offset: int = 0) \
            -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()

        _filters = list()
        if user.role is not UserRole.MASTER:
            _filters.append(ProjectUser.user == user)
        else:
            if 'user_id' in filters:
                _filters.append(ProjectUser.user == filters['user_id'])

        if 'build_id' in filters:
            _filters.append(Stage.build == filters['build_id'])
        if 'status' in filters:
            _filters.append(Stage.status == StageStatus.from_str(filters['status']))
        if 'created' in filters:
            _filters.append(Stage.created == filters['created'])
        if 'min-created' in filters:
            _filters.append(Stage.created >= filters['min-created'])
        if 'max-created' in filters:
            _filters.append(Stage.created <= filters['max-created'])

        _order = list()
        for o in order:
            if o == 'created-desc':
                _order.append(Stage.id.desc())
            if o == 'created-asc':
                _order.append(Stage.id.asc())
        if len(_order) == 0:
            _order.append(Stage.id.desc())

        query = Stage.select(Stage).distinct()
        if ('user_id' in filters and user.role is UserRole.MASTER) or user.role is not UserRole.MASTER:
            query = query.join(Build).join(ProjectUser, on=(Build.project == ProjectUser.project))
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.limit(offset)
        query = query.order_by(*_order)

        result = list()
        for stage in query:
            result.append({
                'id': stage.id,
                'build': stage.build.id,
                'status': stage.status.to_str(),
                'name': stage.name,
                'order': stage.order,
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

        if 'build_id' in filters:
            _filters.append(Stage.build == filters['build_id'])
        if 'status' in filters:
            _filters.append(Stage.status == StageStatus.from_str(filters['status']))
        if 'created' in filters:
            _filters.append(Stage.created == filters['created'])
        if 'min-created' in filters:
            _filters.append(Stage.created >= filters['min-created'])
        if 'max-created' in filters:
            _filters.append(Stage.created <= filters['max-created'])

        query = Stage.select(Stage).distinct()
        if ('user_id' in filters and user.role is UserRole.MASTER) or user.role is not UserRole.MASTER:
            query = query.join(Build).join(ProjectUser, on=(Build.project == ProjectUser.project))
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.wrapped_count()

    @staticmethod
    def cancel(user: User, idx: int) -> None:
        try:
            stage = Stage.get(Stage.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                project_role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == stage.build.project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied
            if project_role not in [ProjectRole.MASTER, ProjectRole.DEVELOPER]:
                raise RepositoryPermissionDenied

        stage.status = StageStatus.CANCELED
        stage.save()
