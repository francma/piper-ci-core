from typing import List, Dict, Any
import functools
import operator

from peewee import DoesNotExist

from piper_core.utils.exceptions import *
from piper_core.model.stages import *
from piper_core.model.projects import *
from piper_core.model.users import *
from piper_core.model.builds import *


class StagesFacade:

    def __init__(self, queue):
        self.queue = queue

    def get(self, user: User, idx) -> Dict[Any, Any]:
        try:
            stage = Stage.get(Stage.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        result = {
            'id': stage.id,
            'build_id': stage.build.id,
            'status': stage.status.to_str(),
            'name': stage.name,
            'order': stage.order,
        }

        return result

    def list(self, user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10,
             offset: int = 0) -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()

        _filters = list()
        if 'build_id' in filters:
            _filters.append(Stage.build == filters['build_id'])
        if 'status' in filters:
            _filters.append(Stage.status == Status.from_str(filters['status']))

        _order = list()
        for o in order:
            if o == 'created-desc':
                _order.append(Stage.id.desc())
            if o == 'created-asc':
                _order.append(Stage.id.asc())
            if o == 'order-desc':
                _order.append(Stage.order.desc())
            if o == 'order-asc':
                _order.append(Stage.order.asc())
        if len(_order) == 0:
            _order.append(Stage.id.desc())

        query = Stage.select(Stage).distinct()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        query = query.order_by(*_order)

        result = list()
        for stage in query:
            result.append({
                'id': stage.id,
                'build_id': stage.build.id,
                'status': stage.status.to_str(),
                'name': stage.name,
                'order': stage.order,
            })

        return result

    def count(self, user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()

        _filters = list()
        if 'build_id' in filters:
            _filters.append(Stage.build == filters['build_id'])
        if 'status' in filters:
            _filters.append(Stage.status == Status.from_str(filters['status']))

        query = Stage.select(Stage).distinct()
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.wrapped_count()

    def cancel(self, user: User, idx: int) -> None:
        from piper_core.model.jobs.job import Job
        try:
            stage: Stage = Stage.get(Stage.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == stage.build.project))
            except DoesNotExist:
                raise FacadeUnauthorized

        if stage.status not in Status.cancelable_statuses():
            raise FacadeInvalidAction

        stage.cancel()
        next_stage: Stage = Stage.get((Stage.build == stage.build) & (Stage.order == stage.order + 1))
        if not next_stage or next_stage.status is not Status.READY:
            return

        jobs = Job.select().where(Job.stage == next_stage)
        for job in jobs:
            self.queue.push(job)

    def restart(self, user: User, idx: int) -> None:
        from piper_core.model.jobs.job import Job

        try:
            stage = Stage.get(Stage.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == stage.build.project))
            except DoesNotExist:
                raise FacadeUnauthorized

        if stage.status not in Status.final_statuses():
            raise FacadeInvalidAction

        stage.restart()
        jobs: List[Job] = Job.select().where((Job.stage == stage) & (Job.status == Status.READY))

        for job in jobs:
            self.queue.push(job)
