import flask

from piper_driver.views.helpers import authorize, query_parse
from piper_driver.repository import StagesRepository

stages_view = flask.Blueprint('stages_view', __name__)


@stages_view.route('/stages', methods=['GET'])
@stages_view.route('/projects/<int:project_id>/stages', methods=['GET'])
@stages_view.route('/builds/<int:build_id>/stages', methods=['GET'])
@query_parse
@authorize
def stages_view_list(filters, order, limit, offset, user, project_id=None, build_id=None):
    if project_id is not None:
        filters['project_id'] = project_id
    elif build_id is not None:
        filters['build_id'] = build_id
    return flask.jsonify(StagesRepository.list(user, filters, order, limit, offset))


@stages_view.route('/stages/<int:stage_id>', methods=['GET'])
@authorize
def stages_view_get(user, stage_id: int):
    return flask.jsonify(StagesRepository.get(user, stage_id))


@stages_view.route('/stages/<int:stage_id>/cancel', methods=['POST'])
@authorize
def stages_view_cancel(user, stage_id: int):
    StagesRepository.cancel(stage_id, user)
    return '', 200
