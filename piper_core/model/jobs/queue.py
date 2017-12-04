from typing import Optional

from peewee import DoesNotExist

from piper_core.model.jobs.job import Job
from piper_core.model.runners.runner import Runner


class JobQueue:

    def __init__(self, connection):
        self.connection = connection

    def push(self, job: Job) -> None:
        queue_name = job.group
        item = str(job.id)
        self.connection.push(queue_name, item)

    def pop(self, runner: Runner) -> Optional[Job]:
        queue_name = runner.group
        job_id = self.connection.pop(queue_name)
        if job_id is None:
            return None

        try:
            job = Job.get(Job.id == int(job_id))
        except DoesNotExist:
            return None

        return job
