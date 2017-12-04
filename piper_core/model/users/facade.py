import operator
from typing import Dict, List
from typing import Any

import functools
from jsonschema import Draft4Validator, ValidationError
from peewee import DoesNotExist, IntegrityError

from piper_core.model.users import *
from piper_core.utils.exceptions import *


class UsersFacade:

    def __init__(self, schema):
        self.schema = schema

    def get(self, user: User, idx: int) -> Dict[Any, Any]:
        try:
            user_a: User = User.get(User.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role not in [UserRole.MASTER, UserRole.ADMIN] and user.id != idx:
            raise FacadeUnauthorized

        result = {
            'id': user_a.id,
            'email': user_a.email,
            'role': user_a.role.to_str(),
            'token': user_a.token,
            'public_key': user_a.public_key,
        }

        return result

    def count(self, user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()

        if user.role not in [UserRole.MASTER, UserRole.ADMIN]:
            raise FacadeUnauthorized

        _filters = list()
        if 'email' in filters:
            _filters.append(User.email == filters['email'])

        _order: List = []
        if len(_order) == 0:
            _order.append(User.id.desc())

        query = User.select(User).distinct()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.wrapped_count()

    def list(self, user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10,
             offset: int = 0) -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else []

        if user.role not in [UserRole.MASTER, UserRole.ADMIN]:
            raise FacadeUnauthorized

        _filters = list()
        if 'email' in filters:
            _filters.append(User.email == filters['email'])

        _order: List = []
        if len(_order) == 0:
            _order.append(User.id.desc())

        query = User.select(User).distinct()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.limit(offset)
        users: List[User] = query.order_by(*_order)

        result = list()
        for item in users:
            result.append({
                'id': item.id,
                'email': item.email,
                'role': item.role.to_str(),
                'token': item.token,
            })

        return result

    def create(self, user: User, values: Dict[str, Any]) -> int:
        if user.role not in [UserRole.MASTER, UserRole.ADMIN]:
            raise FacadeUnauthorized

        self._validate_user_schema(values)
        role = UserRole.from_str(values['role'])

        if user.role is UserRole.ADMIN and role is not UserRole.NORMAL:
            raise FacadeUnauthorized

        user_a = User()
        user_a.email = values['email']
        user_a.role = UserRole.from_str(values['role'])
        user_a.public_key = values['public_key']

        try:
            user_a.save()
        except IntegrityError:
            raise FacadeIntegrityError('User must be unique')

        return user_a.id

    def delete(self, user: User, idx: int) -> None:
        try:
            User.get(User.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role not in [UserRole.MASTER] and user.id != idx:
            raise FacadeUnauthorized

        User.delete().where(User.id == idx).execute()

    def update(self, user: User, idx: int, values: Dict[str, Any]) -> None:
        try:
            user_a: User = User.get(User.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role not in [UserRole.MASTER] and user.id != idx:
            raise FacadeUnauthorized

        self._validate_user_schema(values)
        role = UserRole.from_str(values['role'])

        if user.role not in [UserRole.MASTER] and user_a.role is not role:
            raise FacadeUnauthorized

        user_a.email = values['email']
        user_a.public_key = values['public_key']
        user_a.role = role

        if 'token' in values:
            user_a.token = values['token']

        try:
            user_a.save()
        except IntegrityError:
            raise FacadeIntegrityError('User must be unique')

    def _validate_user_schema(self, values):
        schema = self.schema['components']['schemas']['user']
        try:
            Draft4Validator(schema=schema).validate(values)
        except ValidationError as e:
            raise Exception(e.message)
