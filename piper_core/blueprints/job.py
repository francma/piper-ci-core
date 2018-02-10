import re
from http import HTTPStatus
import sys

import flask
from peewee import DoesNotExist

from piper_core.blueprints.helpers import authorize, query_parse
from piper_core.model import *
from piper_core.utils.exceptions import *


class JobBlueprintFactory:

    @staticmethod
    def create(facade: JobsFacade, queue: JobQueue):
        blueprint = flask.Blueprint('jobs', __name__)

        @blueprint.route('/jobs', methods=['GET'])
        @blueprint.route('/projects/<int:project_id>/jobs', methods=['GET'])
        @blueprint.route('/builds/<int:build_id>/jobs', methods=['GET'])
        @blueprint.route('/stages/<int:stage_id>/jobs', methods=['GET'])
        @query_parse
        @authorize
        def jobs_view_list(filters, order, limit, offset, user, project_id=None, build_id=None, stage_id=None):
            if project_id is not None:
                filters['project_id'] = project_id
            elif build_id is not None:
                filters['build_id'] = build_id
            elif stage_id is not None:
                filters['stage_id'] = stage_id
            return flask.jsonify(facade.list(user, filters, order, limit, offset))

        @blueprint.route('/jobs/<int:job_id>', methods=['GET'])
        @authorize
        def jobs_view_get(user, job_id: int):
            return flask.jsonify(facade.get(user, job_id))

        @blueprint.route('/jobs/<int:job_id>/cancel', methods=['POST'])
        @authorize
        def jobs_view_cancel(user, job_id: int):
            facade.cancel(user, job_id)
            return '', HTTPStatus.OK

        @blueprint.route('/jobs/<int:job_id>/restart', methods=['POST'])
        @authorize
        def jobs_view_restart(user, job_id: int):
            facade.restart(user, job_id)
            return '', HTTPStatus.OK

        @blueprint.route('/jobs/queue/<runner_token>', methods=['GET'])
        def jobs_view_queue_pop(runner_token: str):
            try:
                runner = Runner.get(Runner.token == runner_token)
            except DoesNotExist:
                return '', HTTPStatus.OK

            while True:
                job = queue.pop(runner)
                # no job is available
                if job is None:
                    break
                # skip not ready jobs (probably inconsistent queue)
                if job.status is not Status.READY:
                    continue

                try:
                    if job.evaluate_only():
                        break
                    else:
                        job.status = Status.SKIPPED
                        job.save()
                        continue
                except JobExpressionException:
                    job.status = Status.ERROR
                    job.note = 'Error on "when" eval'
                    job.save()
                    continue

            if job is None:
                return '', HTTPStatus.OK

            job.status = Status.RUNNING
            job.save()
            export: Job = Job.get(Job.id == job.id)

            return flask.jsonify(export.export())

        @blueprint.route('/jobs/report/<secret>', methods=['POST'])
        def jobs_view_report(secret: str):
            try:
                job = Job.get(Job.secret == secret)
            except DoesNotExist:
                return flask.jsonify({'status': ResponseStatus.ERROR.value})

            try:
                runner_status = RequestStatus[flask.request.args.get('status')]
            except KeyError:
                return '', HTTPStatus.OK

            if runner_status is RequestStatus.RUNNING:
                if job.status is Status.CANCELED:
                    return flask.jsonify({'status': ResponseStatus.CANCEL.value})
                if job.status is not Status.RUNNING:
                    return flask.jsonify({'status': ResponseStatus.ERROR.value})

                facade.append_log(job, flask.request.data)

                return flask.jsonify({'status': ResponseStatus.OK.value})
            elif runner_status is RequestStatus.ERROR:
                job.status = Status.ERROR
                job.save()
                return flask.jsonify({'status': ResponseStatus.ERROR.value})
            elif runner_status is RequestStatus.COMPLETED:
                facade.append_log(job, flask.request.data)

                # is there a failed command?
                try:
                    failed = Command.get(
                        (Command.job == job) &
                        (Command.return_code != 0) &
                        (Command.type == CommandType.NORMAL)
                    ).order
                except DoesNotExist:
                    failed = sys.maxsize

                # are all commands before failed one completed?
                uncompleted = Command.select().where(
                    (Command.job == job) &
                    (Command.return_code.is_null()) &
                    (Command.order < failed) &
                    (Command.type == CommandType.NORMAL)
                )

                if uncompleted.count():
                    job.status = Status.ERROR
                    job.save()

                    return flask.jsonify({'status': ResponseStatus.ERROR.value})

                # check if all after_failure commands are executed
                if failed:
                    uncompleted = Command.select().where(
                        (Command.job == job) &
                        (Command.return_code.is_null()) &
                        (Command.type == CommandType.AFTER_FAILURE)
                    )

                    if uncompleted.count():
                        job.status = Status.ERROR
                        job.save()

                        return flask.jsonify({'status': ResponseStatus.ERROR.value})

                job.status = Status.FAILED if failed != sys.maxsize else Status.SUCCESS
                job.save()

                # Push Jobs from next stage if current stage == SUCCESS
                jobs = Job.select().join(Stage).join(Build).where(
                    (Stage.order == job.stage.order + 1) &
                    (Job.status == Status.READY) &
                    (Build.id == job.stage.build.id)
                )
                for job in jobs:
                    queue.push(job)

                return flask.jsonify({'status': ResponseStatus.OK.value})

        @blueprint.route('/jobs/<int:job_id>/log', methods=['GET'])
        @authorize
        def jobs_view_log(user: User, job_id: int):
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

            data = facade.read_log(user, job_id, offset, limit)

            status = HTTPStatus.PARTIAL_CONTENT if range_header else HTTPStatus.OK
            rv = flask.Response(data, status, mimetype='text/plain', direct_passthrough=True)
            rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(offset, offset + len(data) - 1, len(data)))

            return rv

        return blueprint
