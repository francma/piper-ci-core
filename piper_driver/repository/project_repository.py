import functools
import operator
from typing import List, Dict, Any


from peewee import DoesNotExist

from piper_driver.repository.repository import Repository
from piper_driver.models import *
from piper_driver.addins.exceptions import *


class ProjectRepository(Repository):

    @staticmethod
    def get(user: User, idx) -> Dict[Any, Any]:
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
    def count(user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()

        _filters = list()
        if user.role is not UserRole.MASTER:
            _filters.append((ProjectUser.user == user))
        else:
            if 'user' in filters:
                _filters.append((ProjectUser.user.id == filters['user']))

        if 'url' in filters:
            _filters.append((Project.url == filters['url']))
        if 'origin' in filters:
            _filters.append((Project.origin == filters['origin']))

        query = Project.select(Project)
        if ('user' in filters and user.role is UserRole.MASTER) or user.role is not UserRole.MASTER:
            query = query.join(ProjectUser)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.wrapped_count()

    @staticmethod
    def list(user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10, offset: int = 0) \
            -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()

        _filters = list()
        if user.role is not UserRole.MASTER:
            _filters.append(ProjectUser.user == user)
        else:
            if 'user' in filters:
                _filters.append(ProjectUser.user.id == filters['user'])

        if 'url' in filters:
            _filters.append(Project.url == filters['url'])
        if 'origin' in filters:
            _filters.append(Project.origin == filters['origin'])

        _order = list()
        for o in order:
            if o == 'created-desc':
                _order.append(Project.id.desc())
            if o == 'created-asc':
                _order.append(Project.id.asc())
        if len(_order) == 0:
            _order.append(Project.id.desc())

        query = Project.select(Project).distinct()
        if ('user' in filters and user.role is UserRole.MASTER) or user.role is not UserRole.MASTER:
            query = query.join(ProjectUser)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.limit(offset)
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
    def update(user: User, idx, values: Dict[str, Any]) -> None:
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
    def create(user: User, values: Dict[str, Any]) -> int:
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
    def delete(user: User, idx: int) -> None:
        try:
            project = Project.get(Project.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                project_role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied

            if project_role not in {ProjectRole.MASTER}:
                raise RepositoryPermissionDenied

        Project.delete().where(Project.id == idx).execute()

    @staticmethod
    def user_list(user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10,
                  offset: int = 0) \
            -> List[Dict[Any, Any]]:
        pass

    @staticmethod
    def user_add(user: User, values: Dict[str, Any]) -> int:
        try:
            project_id = int(values['project'])
        except (KeyError, ValueError):
            raise RepositoryException
        try:
            user_id = int(values['user'])
        except (KeyError, ValueError):
            raise RepositoryException
        try:
            role = ProjectRole.from_str(values['role'])
        except (KeyError, ValueError):
            raise RepositoryException

        try:
            project = Project.get(Project.id == project_id)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                project_role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied
            if project_role is not ProjectRole.MASTER:
                raise RepositoryPermissionDenied

        try:
            project_user = User.get(User.id == user_id)
        except DoesNotExist:
            raise RepositoryNotFound

        if project_user.role not in [UserRole.MASTER, UserRole.ADMIN] and role is ProjectRole.MASTER:
            raise RepositoryException

        ProjectUser.create(user=project_user, project=project, role=role)

        return project_user.id

    @staticmethod
    def user_remove(user: User, values: Dict[str, Any]) -> None:
        try:
            project_id = int(values['project'])
        except (KeyError, ValueError):
            raise RepositoryException
        try:
            user_id = int(values['user'])
        except (KeyError, ValueError):
            raise RepositoryException
        try:
            project_user = User.get(User.id == user_id)
        except DoesNotExist:
            raise RepositoryNotFound

        try:
            project = Project.get(Project.id == project_id)
        except DoesNotExist:
            raise RepositoryNotFound

        if user.role is not UserRole.MASTER:
            try:
                project_role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise RepositoryPermissionDenied
            if project_role is not ProjectRole.MASTER:
                raise RepositoryPermissionDenied

        try:
            ProjectUser.delete().where((ProjectUser.project == project) & (ProjectUser.user == project_user)).execute()
        except DoesNotExist:
            raise RepositoryNotFound
