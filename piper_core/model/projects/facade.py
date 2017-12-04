import functools
import operator
from typing import List, Dict, Any

from jsonschema import Draft4Validator, ValidationError
from peewee import DoesNotExist, IntegrityError

from piper_core.utils.exceptions import *
from piper_core.model.users import *
from piper_core.model.projects import *
from piper_core.utils.git import validate_origin


class ProjectsFacade:

    def __init__(self, schema):
        self.schema = schema

    def get(self, user: User, idx) -> Dict[Any, Any]:
        try:
            project = Project.get(Project.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        result = {
            'id': project.id,
            'origin': project.origin,
            'url': project.url,
            'status': str(project.status),
        }

        return result

    def count(self, user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()

        _filters = list()
        if 'url' in filters:
            _filters.append((Project.url == filters['url']))
        if 'origin' in filters:
            _filters.append((Project.origin == filters['origin']))
        if 'status' in filters:
            _filters.append((Project.status == ProjectStatus.from_str(filters['status'])))

        query = Project.select(Project)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.wrapped_count()

    def list(self, user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10,
             offset: int = 0) -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()

        _filters = list()
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
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        query = query.order_by(*_order)

        result = list()
        for project in query:
            result.append({
                'id': project.id,
                'origin': project.origin,
                'url': project.url,
                'status': project.status.to_str(),
            })

        return result

    def update(self, user: User, idx, values: Dict[str, Any]) -> None:
        try:
            project = Project.get(Project.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise FacadeUnauthorized
            if role is not ProjectRole.MASTER:
                raise FacadeUnauthorized

        self._validate_project_schema(values)

        project.origin = values['origin']
        project.url = values['url']
        try:
            project.save()
        except IntegrityError:
            raise FacadeIntegrityError('Project origin must be unique')

    def create(self, user: User, values: Dict[str, Any]) -> int:
        if user.role not in [UserRole.MASTER, UserRole.ADMIN]:
            raise FacadeUnauthorized

        self._validate_project_schema(values)

        project = Project()
        project.origin = values['origin']
        project.url = values['url']

        try:
            project.save()
        except IntegrityError:
            raise FacadeIntegrityError('Project origin must be unique')

        ProjectUser.create(role=ProjectRole.MASTER, user=user, project=project)

        return project.id

    def delete(self, user: User, idx: int) -> None:
        try:
            project = Project.get(Project.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise FacadeUnauthorized
            if role is not ProjectRole.MASTER:
                raise FacadeUnauthorized

        Project.delete().where(Project.id == idx).execute()

    def user_list(self, user: User, project_id: int) -> List[Dict[Any, Any]]:
        try:
            project = Project.get(Project.id == project_id)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                project_role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise FacadeUnauthorized
            if project_role is not ProjectRole.MASTER:
                raise FacadeUnauthorized

        query: List[User] = User.select(User).join(ProjectUser).where(ProjectUser.project == project)

        result = list()
        for item in query:
            result.append({
                'id': item.id,
                'email': item.email,
                'role': ProjectUser.get(ProjectUser.user == item).role
            })

        return result

    def user_add(self, user: User, values: Dict[str, Any]) -> int:
        self._validate_user_modify_schema(values)
        role = ProjectRole.from_str(values['role'])

        try:
            project = Project.get(Project.id == values['project_id'])
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                project_role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise FacadeUnauthorized
            if project_role is not ProjectRole.MASTER:
                raise FacadeUnauthorized

        try:
            project_user = User.get(User.id == values['user_id'])
        except DoesNotExist:
            raise FacadeNotFound

        ProjectUser.create(user=project_user, project=project, role=role)

        return project_user.id

    def user_remove(self, user: User, values: Dict[str, Any]) -> None:
        self._validate_user_remove_schema(values)
        try:
            project_user = User.get(User.id == values['user_id'])
        except DoesNotExist:
            raise FacadeNotFound

        try:
            project = Project.get(Project.id == values['project_id'])
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                project_role = ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == project)).role
            except DoesNotExist:
                raise FacadeUnauthorized
            if project_role is not ProjectRole.MASTER:
                raise FacadeUnauthorized

        try:
            ProjectUser.delete().where((ProjectUser.project == project) & (ProjectUser.user == project_user)).execute()
        except DoesNotExist:
            raise FacadeNotFound

    def _validate_user_modify_schema(self, values):
        schema = self.schema['components']['schemas']['project-user-modify']
        try:
            Draft4Validator(schema=schema).validate(values)
        except ValidationError as e:
            raise FacadeInvalidSchema(e.message)

    def _validate_user_remove_schema(self, values):
        schema = self.schema['components']['schemas']['project-user-remove']
        try:
            Draft4Validator(schema=schema).validate(values)
        except ValidationError as e:
            raise FacadeInvalidSchema(e.message)

    def _validate_project_schema(self, values):
        schema = self.schema['components']['schemas']['project']
        try:
            Draft4Validator(schema=schema).validate(values)
        except ValidationError as e:
            raise FacadeInvalidSchema(e.message)

        if not validate_origin(values['origin']):
            raise FacadeInvalidSchema('Invalid origin')
