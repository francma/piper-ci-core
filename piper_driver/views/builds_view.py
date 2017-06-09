import flask

from piper_driver.views.helpers import authorize, query_parse
from piper_driver.repository import BuildsRepository

builds_view = flask.Blueprint('builds_view', __name__)


@builds_view.route('/builds', methods=['GET'])
@builds_view.route('/projects/<int:project_id>/builds', methods=['GET'])
@query_parse
@authorize
def builds_view_list(filters, order, limit, offset, user, project_id=None):
    if project_id is not None:
        filters['project_id'] = project_id
    return flask.jsonify(BuildsRepository.list(user, filters, order, limit, offset))


@builds_view.route('/builds/<int:build_id>', methods=['GET'])
@authorize
def builds_view_get(user, build_id: int):
    return flask.jsonify(BuildsRepository.get(user, build_id))


@builds_view.route('/builds/<int:build_id>/cancel', methods=['POST'])
@authorize
def builds_view_update(user, build_id: int):
    BuildsRepository.cancel(user, build_id)
    return '', 200
