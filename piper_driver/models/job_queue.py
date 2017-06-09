from typing import Optional

from peewee import DoesNotExist

from piper_driver.addins.queue import Queue
from piper_driver.models import Job, Runner


class JobQueue(Queue):

    @staticmethod
    def push(job: Job) -> None:
        queue_name = job.group
        item = str(job.id)
        super(JobQueue, JobQueue).push(queue_name, item)

    @staticmethod
    def pop(runner: Runner) -> Optional[Job]:
        queue_name = runner.group
        job_id = super(JobQueue, JobQueue).pop(queue_name)
        if job_id is None:
            return None

        try:
            job = Job.get(Job.id == int(job_id))
        except DoesNotExist:
            return None

        return job
