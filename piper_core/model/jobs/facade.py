import functools
import operator
from typing import List, Dict, Any

from pathlib import Path
import re
import sys

from piper_core.utils.exceptions import *
from piper_core.model.users import *
from piper_core.model.projects import *
from piper_core.model.jobs import *
from piper_core.model.builds import *
from piper_core.model.stages import *


from peewee import DoesNotExist


class JobsFacade:

    def __init__(self, job_log_dir: Path, queue: JobQueue) -> None:
        self.job_log_dir = job_log_dir
        self.queue = queue

    def _job_detail(self, job: Job):
        def export_command(c: Command):
            return {
                'cmd': c.cmd,
                'log_start': c.log_start,
                'log_end': c.log_end,
                'start': c.start,
                'end': c.end,
                'return_code': c.return_code,
            }

        commands = []
        for command in job.commands:
            commands.append(export_command(command))

        after_failure = []
        for command in job.after_failure:
            after_failure.append(export_command(command))

        result = {
            'id': job.id,
            'stage_id': job.stage.id,
            'status': str(job.status),
            'group': job.group,
            'image': job.image,
            'only': job.only,
            'commands': commands,
            'after_failure': after_failure,
            'env': job.environment,
            'note': job.note,
        }

        return result

    def get(self, user: User, idx: int) -> Dict[Any, Any]:
        try:
            job: Job = Job.get(Job.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        return self._job_detail(job)

    def list(self, user: User, filters: Dict[str, Any] = None, order: List[str] = None, limit: int = 10,
             offset: int = 0) -> List[Dict[Any, Any]]:
        filters = filters if filters else dict()
        order = order if order else list()

        _filters = list()

        if 'project_id' in filters:
            _filters.append((Project.id == filters['project_id']))
        if 'status' in filters:
            _filters.append((Job.status == Status.from_str(filters['status'])))
        if 'build_id' in filters:
            _filters.append((Build.id == filters['build_id']))
        if 'stage_id' in filters:
            _filters.append((Job.stage == filters['stage_id']))

        _order = list()
        for o in order:
            if o == 'created-desc':
                _order.append(Job.id.desc())
            if o == 'created-asc':
                _order.append(Job.id.asc())
        if len(_order) == 0:
            _order.append(Job.id.desc())

        result = list()
        query = Job.select(Job).distinct().join(Stage).join(Build).join(Project)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))
        query = query.order_by(*_order)
        query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        for job in query:
            result.append(self._job_detail(job))

        return result

    def count(self, user: User, filters: Dict[str, Any] = None) -> int:
        filters = filters if filters else dict()

        _filters = list()

        if 'project_id' in filters:
            _filters.append((Project.id == filters['project_id']))
        if 'status' in filters:
            _filters.append((Job.status == Status.from_str(filters['status'])))
        if 'build_id' in filters:
            _filters.append((Build.id == filters['build_id']))

        query = Job.select(Job).distinct().join(Stage).join(Build).join(Project)
        if len(_filters) > 0:
            query = query.where(functools.reduce(operator.and_, _filters))

        return query.wrapped_count()

    def cancel(self, user: User, idx: int) -> None:
        try:
            job = Job.get(Job.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == job.stage.build.project))
            except DoesNotExist:
                raise FacadeUnauthorized

        if job.status not in Status.cancelable_statuses():
            raise FacadeInvalidAction

        job.status = Status.CANCELED
        job.save()

        next_stage: Stage = Stage.get((Stage.build == job.stage.build) & (Stage.order == job.stage.order + 1))
        if not next_stage or next_stage.status is not Status.READY:
            return

        jobs = Job.select().where(Job.stage == next_stage)
        for job in jobs:
            self.queue.push(job)

    def restart(self, user: User, idx: int) -> None:
        try:
            job: Job = Job.get(Job.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        if user.role is not UserRole.MASTER:
            try:
                ProjectUser.get((ProjectUser.user == user) & (ProjectUser.project == job.stage.build.project)).role
            except DoesNotExist:
                raise FacadeUnauthorized

        if job.status not in Status.final_statuses():
            raise FacadeInvalidAction

        job.status = Status.READY
        job.save()

        log_path = self.job_log_dir / str(job.id)
        if log_path.exists():
            log_path.unlink()

        self.queue.push(job)

    def _job_log_path(self, job: Job) -> Path:
        log_path = self.job_log_dir / (str(job.id) + str(job.secret))

        return log_path

    def read_log(self, user: User, idx, offset: int=0, limit: int=None) -> bytes:
        try:
            job = Job.get(Job.id == idx)
        except DoesNotExist:
            raise FacadeNotFound

        log_path = self._job_log_path(job)
        if not log_path.exists():
            return b''

        if limit is None:
            limit = sys.maxsize

        with open(log_path, 'rb') as fp:
            if offset is not None:
                fp.seek(offset)

            lines = []
            while limit:
                line = fp.readline(limit)
                if not line:
                    break
                lines.append(line)
                limit -= len(line)

        last = lines[-1] if len(lines) else None
        if last and last[0] == ord(':') and last[-1] != ord('\n'):
            lines = lines[:-1]

        return b''.join(lines)

    def append_log(self, job: Job, contents: bytes):
        from piper_core.model.jobs.command import Command, CommandType

        def get_command(_order: int, _typeof: str) -> Command:
            if _typeof == b'command':
                command_type = CommandType.NORMAL
            elif _typeof == b'after_failure':
                command_type = CommandType.AFTER_FAILURE

            return Command.get((Command.job == job) & (Command.order == _order) & (Command.type == command_type))

        log_path = self._job_log_path(job)
        if log_path.exists():
            log_size = log_path.stat().st_size
        else:
            log_size = 0

        it = re.finditer(Job.COMMAND_BEGIN.encode(), contents, re.MULTILINE)
        for m in it:
            typeof, order, start_time = m.group(1), int(m.group(2)), int(m.group(3))
            command = get_command(order, typeof)
            command.start = start_time
            command.log_start = log_size + m.end() + 1
            command.save()

        it = re.finditer(Job.COMMAND_END.encode(), contents, re.MULTILINE)
        for m in it:
            typeof, order, end_time, return_code = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
            command = get_command(order, typeof)
            command.end = end_time
            command.log_end = log_size + m.start() - 1
            command.return_code = return_code
            command.save()

        job.save()

        with log_path.open(mode='ab') as fp:
            fp.write(contents)
            fp.flush()
