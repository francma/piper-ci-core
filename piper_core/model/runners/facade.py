import functools
import operator
from typing import List, Dict, Any

from jsonschema import Draft4Validator, ValidationError
from peewee import DoesNotExist, IntegrityError

from piper_core.utils.exceptions import *
from piper_core.model.runners import *
from piper_core.model.users import *


class RunnersFacade:

    def __init__(self, schema):
        self.schema = schema

    def get(self, user: User, idx: int) -> Dict[Any, Any]:
        try:
            runner = Runner.get(Runner.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role not in [UserRole.MASTER, UserRole.ADMIN, UserRole.NORMAL]:
            raise FacadeUnauthorized

        result = {
            'id': runner.id,
            'group': runner.group,
        }

        if user.role is UserRole.MASTER:
            result['token'] = runner.token

        return result

    def list(self, user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10,
             offset: int = 0) -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()

        if user.role not in [UserRole.MASTER, UserRole.ADMIN, UserRole.NORMAL]:
            raise FacadeUnauthorized

        _filters = list()
        if 'group' in filters:
            _filters.append(Runner.group == filters['group'])

        _order: List[Any] = list()
        if len(_order) == 0:
            _order.append(Runner.id.desc())

        query = Runner.select()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        query = query.order_by(*_order)

        result = list()
        for runner in query:
            row = {
                'id': runner.id,
                'group': runner.group,
            }

            if user.role is UserRole.MASTER:
                row['token'] = runner.token

            result.append(row)

        return result

    def count(self, user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()
        _filters = list()

        if user.role not in [UserRole.MASTER, UserRole.ADMIN, UserRole.NORMAL]:
            raise FacadeUnauthorized

        if 'group' in filters:
            _filters.append(Runner.group == filters['group'])

        query = Runner.select()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.count()

    def update(self, user: User, idx, values: Dict[str, Any]) -> None:
        if user.role is not UserRole.MASTER:
            raise FacadeUnauthorized
        try:
            runner = Runner.get(Runner.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        self._validate_project_schema(values)

        runner.group = values['group']
        runner.token = values['token']

        try:
            runner.save()
        except IntegrityError:
            raise FacadeIntegrityError('Runner token must be unique')

    def create(self, user: User, values: Dict[str, Any]) -> int:
        if user.role is not UserRole.MASTER:
            raise FacadeUnauthorized

        self._validate_project_schema(values)

        runner = Runner()
        runner.group = values['group']
        runner.token = values['token']
        try:
            runner.save()
        except IntegrityError:
            raise FacadeIntegrityError('Runner token must be unique')

        return runner.id

    def delete(self, user: User, idx) -> None:
        if user.role is not UserRole.MASTER:
            raise FacadeUnauthorized

        try:
            Runner.delete().where(Runner.id == idx).execute()
        except DoesNotExist:
            raise FacadeNotFound

    def _validate_project_schema(self, values):
        schema = self.schema['components']['schemas']['runner']
        try:
            Draft4Validator(schema=schema).validate(values)
        except ValidationError as e:
            raise FacadeInvalidSchema(e.message)
