import re
from http import HTTPStatus

import flask
from peewee import DoesNotExist

from piper_driver.views.helpers import authorize, query_parse
from piper_driver.repository import JobRepository
from piper_driver.models import *
from piper_driver.addins.exceptions import *

jobs_view = flask.Blueprint('jobs_view', __name__)


@jobs_view.route('/jobs', methods=['GET'])
@jobs_view.route('/projects/<int:project_id>/jobs', methods=['GET'])
@jobs_view.route('/builds/<int:build_id>/jobs', methods=['GET'])
@jobs_view.route('/stages/<int:stage_id>/jobs', methods=['GET'])
@query_parse
@authorize
def jobs_view_list(filters, order, limit, offset, user, project_id=None, build_id=None, stage_id=None):
    if project_id is not None:
        filters['project_id'] = project_id
    elif build_id is not None:
        filters['build_id'] = build_id
    elif stage_id is not None:
        filters['stage_id'] = stage_id
    return flask.jsonify(JobRepository.list(user, filters, order, limit, offset))


@jobs_view.route('/jobs/<int:job_id>', methods=['GET'])
@authorize
def jobs_view_get(user, job_id: int):
    return flask.jsonify(JobRepository.get(user, job_id))


@jobs_view.route('/jobs/<int:job_id>/cancel', methods=['POST'])
@authorize
def jobs_view_cancel(user, job_id: int):
    JobRepository.cancel(job_id, user)
    return '', HTTPStatus.OK


@jobs_view.route('/jobs/queue/<runner_token>', methods=['GET'])
def jobs_view_queue_pop(runner_token: str):
    try:
        runner = Runner.get(Runner.token == runner_token)
    except DoesNotExist:
        return '', HTTPStatus.NOT_FOUND

    job = JobQueue.pop(runner)
    if job is None:
        return '', HTTPStatus.OK

    job.status = JobStatus.RUNNING

    return flask.jsonify(job.export())


@jobs_view.route('/jobs/report/<secret>', methods=['POST'])
def jobs_view_report(secret: str):
    try:
        job = Job.get(Job.secret == secret)
    except DoesNotExist:
        return flask.jsonify({'status': ResponseJobStatus.ERROR.value})
    try:
        runner_status = RequestJobStatus[flask.request.args.get('status')]
    except KeyError:
        return '', HTTPStatus.OK

    if runner_status is RequestJobStatus.RUNNING:
        if job.status is JobStatus.CANCELED:
            return flask.jsonify({'status': ResponseJobStatus.CANCEL.value})
        if job.status is not JobStatus.RUNNING:
            return flask.jsonify({'status': ResponseJobStatus.ERROR.value})

        JobRepository.append_log(job, flask.request.data)

        return flask.jsonify({'status': ResponseJobStatus.OK.value})

    if runner_status is RequestJobStatus.ERROR:
        job.status = JobStatus.ERROR
        job.save()
        return flask.jsonify({'status': ResponseJobStatus.ERROR.value})

    if runner_status is RequestJobStatus.COMPLETED:
        JobRepository.append_log(job, flask.request.data)
        # TODO we should check logs for actual status
        job.status = JobStatus.SUCCESS
        job.save()
        return flask.jsonify({'status': ResponseJobStatus.OK.value})


@jobs_view.route('/jobs/<int:job_id>/log', methods=['GET'])
@authorize
def jobs_view_log(user, job_id: int):
    range_header = flask.request.headers.get('Range', None)
    offset, limit = 0, None
    if range_header:
        try:
            m = re.match('^bytes (\d+)-(\d*)$', range_header)
            if not m:
                raise ValueError
            g = m.groups()
            offset = int(g[0])
            if g[1]:
                limit = int(g[1]) - offset
        except ValueError:
            return '', HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE

    try:
        data = JobRepository.read_log(user, job_id, offset, limit)
    except DoesNotExist:
        return '', HTTPStatus.NOT_FOUND
    except RepositoryPermissionDenied:
        return '', HTTPStatus.FORBIDDEN

    status = HTTPStatus.PARTIAL_CONTENT if range_header else HTTPStatus.OK
    rv = flask.Response(data, status, mimetype='text/plain', direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(offset, offset + len(data) - 1, len(data)))

    return rv
