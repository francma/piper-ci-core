import flask
from http import HTTPStatus

from piper_core.blueprints.helpers import authorize, query_parse
from piper_core.model import *


class StageBlueprintFactory:

    @staticmethod
    def create(facade: StagesFacade):
        blueprint = flask.Blueprint('stages', __name__)

        @blueprint.route('/stages', methods=['GET'])
        @blueprint.route('/projects/<int:project_id>/stages', methods=['GET'])
        @blueprint.route('/builds/<int:build_id>/stages', methods=['GET'])
        @query_parse
        @authorize
        def stages_view_list(filters, order, limit, offset, user, project_id=None, build_id=None):
            if project_id is not None:
                filters['project_id'] = project_id
            elif build_id is not None:
                filters['build_id'] = build_id
            return flask.jsonify(facade.list(user, filters, order, limit, offset))

        @blueprint.route('/stages/count', methods=['GET'])
        @blueprint.route('/projects/<int:project_id>/stages/count', methods=['GET'])
        @blueprint.route('/builds/<int:build_id>/stages/count', methods=['GET'])
        @authorize
        def stages_view_count(user, project_id=None, build_id=None):
            filters = flask.request.args.items()
            if project_id is not None:
                filters['project_id'] = project_id
            elif build_id is not None:
                filters['build_id'] = build_id

            count = facade.count(user, filters)

            return flask.jsonify({'count': count})

        @blueprint.route('/stages/<int:stage_id>', methods=['GET'])
        @authorize
        def stages_view_get(user, stage_id: int):
            return flask.jsonify(facade.get(user, stage_id))

        @blueprint.route('/stages/<int:stage_id>/cancel', methods=['POST'])
        @authorize
        def stages_view_restart(user, stage_id: int):
            facade.cancel(user, stage_id)
            return '', HTTPStatus.OK

        @blueprint.route('/stages/<int:stage_id>/cancel', methods=['POST'])
        @authorize
        def stages_view_cancel(user, stage_id: int):
            facade.restart(user, stage_id)
            return '', HTTPStatus.OK

        return blueprint
