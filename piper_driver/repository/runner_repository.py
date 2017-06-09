import functools
import operator
from typing import List, Dict, Any

from peewee import DoesNotExist

from piper_driver.repository.repository import Repository
from piper_driver.models import *
from piper_driver.addins.exceptions import *


class RunnerRepository(Repository):

    @staticmethod
    def get(user: User, idx: int) -> Dict[Any, Any]:
        try:
            runner = Runner.get(Runner.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        result = {
            'id': runner.id,
            'group': runner.group,
        }

        if user.role is UserRole.MASTER:
            result['token'] = runner.token

        return result

    @staticmethod
    def list(user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10, offset: int = 0) \
            -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()
        _filters = list()

        if 'group' in filters:
            _filters.append(Runner.group == filters['group'])

        query = Runner.select()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.limit(offset)

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

    @staticmethod
    def count(user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()
        _filters = list()

        if 'group' in filters:
            _filters.append(Runner.group == filters['group'])

        query = Runner.select()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.count()

    @staticmethod
    def update(user: User, idx, values: Dict[str, Any]) -> None:
        if user.role is not UserRole.MASTER:
            raise RepositoryPermissionDenied
        try:
            runner = Runner.get(Runner.id == idx)
        except DoesNotExist:
            raise RepositoryNotFound

        allowed = {'group', 'token'}
        for k, v in values.items():
            if k in allowed:
                setattr(runner, k, v)
        runner.save()

    @staticmethod
    def create(user: User, values: Dict[str, Any]) -> int:
        if user.role is not UserRole.MASTER:
            raise RepositoryPermissionDenied

        runner = Runner()
        allowed = {'group', 'token'}
        for k, v in values.items():
            if k in allowed:
                setattr(runner, k, v)
        runner.save()

        return runner.id

    @staticmethod
    def delete(user: User, idx) -> None:
        if user.role is not UserRole.MASTER:
            raise RepositoryPermissionDenied

        try:
            Runner.delete().where(Runner.id == idx).execute()
        except DoesNotExist:
            raise RepositoryNotFound
