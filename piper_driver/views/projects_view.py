import flask

from piper_driver.views.helpers import authorize, query_parse
from piper_driver.repository import ProjectRepository

projects_view = flask.Blueprint('projects_view', __name__)


@projects_view.route('/projects/<int:project_id>', methods=['GET'])
@authorize
def projects_view_get(user, project_id: int):
    return flask.jsonify(ProjectRepository.get(user, project_id))


@projects_view.route('/projects', methods=['GET'])
@query_parse
@authorize
def projects_view_list(filters, order, limit, offset, user):
    return flask.jsonify(ProjectRepository.list(user, filters, order, limit, offset))


@projects_view.route('/projects', methods=['POST'])
@authorize
def projects_view_create(user):
    ProjectRepository.create(user, flask.request.get_json())
    return '', 201


@projects_view.route('/projects/<int:project_id>', methods=['PUT'])
@authorize
def projects_view_update(user, project_id: int):
    ProjectRepository.update(user, project_id, flask.request.get_json())
    return '', 204


@projects_view.route('/projects/<int:project_id>', methods=['DELETE'])
@authorize
def projects_view_delete(user, project_id: int):
    ProjectRepository.delete(user, project_id)
    return '', 204
