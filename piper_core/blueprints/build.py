import flask
from http import HTTPStatus

from piper_core.blueprints.helpers import authorize, query_parse
from piper_core.model import *


class BuildBlueprintFactory:

    @staticmethod
    def create(facade: BuildsFacade):
        builds_view = flask.Blueprint('builds_view', __name__)

        @builds_view.route('/builds', methods=['GET'])
        @builds_view.route('/projects/<int:project_id>/builds', methods=['GET'])
        @query_parse
        @authorize
        def builds_view_list(filters, order, limit, offset, user, project_id=None):
            if project_id is not None:
                filters['project_id'] = project_id
            return flask.jsonify(facade.list(user, filters, order, limit, offset))

        @builds_view.route('/builds/count', methods=['GET'])
        @builds_view.route('/projects/<int:project_id>/builds/count', methods=['GET'])
        @authorize
        def builds_view_count(user, project_id=None):
            filters = flask.request.args.items()
            if project_id is not None:
                filters['project_id'] = project_id

            count = facade.count(user, filters)

            return flask.jsonify({'count': count})

        @builds_view.route('/builds/<int:build_id>', methods=['GET'])
        @authorize
        def builds_view_get(user, build_id: int):
            return flask.jsonify(facade.get(user, build_id))

        @builds_view.route('/builds/<int:build_id>/cancel', methods=['POST'])
        @authorize
        def builds_view_cancel(user, build_id: int):
            facade.cancel(user, build_id)
            return '', HTTPStatus.OK

        @builds_view.route('/builds/<int:build_id>/restart', methods=['POST'])
        @authorize
        def builds_view_restart(user, build_id: int):
            facade.restart(user, build_id)
            return '', HTTPStatus.OK

        return builds_view
