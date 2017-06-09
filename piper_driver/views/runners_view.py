import flask

from piper_driver.views.helpers import authorize, query_parse
from piper_driver.repository import RunnerRepository

runners_view = flask.Blueprint('runners_view', __name__)


@runners_view.route('/runners/<int:runner_id>', methods=['GET'])
@authorize
def runners_view_get(user, runner_id: int):
    return flask.jsonify(RunnerRepository.get(user, runner_id))


@runners_view.route('/runners', methods=['GET'])
@query_parse
@authorize
def runners_view_list(filters, order, limit, offset, user):
    return flask.jsonify(RunnerRepository.list(user, filters, order, limit, offset))


@runners_view.route('/runners', methods=['POST'])
@authorize
def runners_view_create(user):
    RunnerRepository.create(user, flask.request.get_json())
    return '', 201


@runners_view.route('/runners/<int:runner_id>', methods=['PUT'])
@authorize
def runners_view_update(user, runner_id: int):
    RunnerRepository.update(user, runner_id, flask.request.get_json())
    return '', 204


@runners_view.route('/runners/<int:project_id>', methods=['DELETE'])
@authorize
def runners_view_delete(user, project_id: int):
    RunnerRepository.delete(user, project_id)
    return '', 204
