from typing import List, Dict, Any
import functools
import operator

from peewee import DoesNotExist

from piper_driver.repository.repository import Repository
from piper_driver.models import *


class ProjectRepository(Repository):

    @staticmethod
    def get(idx, user: User) -> Dict[Any, Any]:
        try:
            project = Project.get(Project.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied

        result = {
            'id': project.id,
            'origin': project.origin,
            'url': project.url,
        }

        return result

    @staticmethod
    def count(filters: Dict[str, Any], user: User, master: bool) -> int:
        pass

    @staticmethod
    def list(filters: Dict[str, Any], order: List[str], limit: int, offset: int, user: User) -> List[Dict[Any, Any]]:
        _filters = list()
        if user.role is not UserRole.MASTER:
            _filters.append((ProjectUser.user == user))
        else:
            if 'user_id' in filters:
                _filters.append((ProjectUser.user.id == filters['user_id']))

        if 'url' in filters:
            _filters.append((Project.url == filters['url']))
        if 'origin' in filters:
            _filters.append((Project.origin == filters['origin']))

        _order = list()
        for o in order:
            if o == 'created-desc':
                _order.append(Project.id.desc())
            if o == 'created-asc':
                _order.append(Project.id.asc())
        if len(_order) == 0:
            _order.append(Project.id.desc())

        query = Project.select(Project).distinct()
        if user.role is not UserRole.MASTER or (user.role is UserRole.MASTER and 'user_id' in filters):
            query = query.join(ProjectUser)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.order_by(*_order)

        result = list()
        for project in query:
            result.append({
                'id': project.id,
                'origin': project.origin,
                'url': project.url,
            })

        return result

    @staticmethod
    def update(idx, values: Dict[str, Any], user: User) -> None:
        try:
            project = Project.get(Project.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied

        allowed = {'origin', 'url'}
        for k, v in values.items():
            if k in allowed:
                setattr(project, k, v)
        project.save()

    @staticmethod
    def create(values: Dict[str, Any], user: User) -> int:
        if user.role not in [UserRole.MASTER, UserRole.ADMIN]:
            raise RepositoryPermissionDenied

        allowed = {'origin', 'url'}
        project = Project()
        for k, v in values.items():
            if k in allowed:
                project.__setattr__(k, v)
        project.save()
        ProjectUser.create(role=ProjectRole.MASTER, user=user, project=project)

        return project.id

    @staticmethod
    def delete(idx, user) -> None:
        pass

