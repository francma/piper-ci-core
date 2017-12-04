import flask
from http import HTTPStatus

from piper_core.blueprints.helpers import authorize, query_parse
from piper_core.model import *


class RunnerBlueprintFactory:

    @staticmethod
    def create(facade: RunnersFacade):
        blueprint = flask.Blueprint('runners_view', __name__)

        @blueprint.route('/runners/<int:runner_id>', methods=['GET'])
        @authorize
        def runners_view_get(user, runner_id: int):
            return flask.jsonify(facade.get(user, runner_id))

        @blueprint.route('/runners', methods=['GET'])
        @query_parse
        @authorize
        def runners_view_list(filters, order, limit, offset, user):
            return flask.jsonify(facade.list(user, filters, order, limit, offset))

        @blueprint.route('/runners', methods=['POST'])
        @authorize
        def runners_view_create(user):
            facade.create(user, flask.request.get_json())
            return '', HTTPStatus.CREATED

        @blueprint.route('/runners/<int:runner_id>', methods=['PUT'])
        @authorize
        def runners_view_update(user, runner_id: int):
            facade.update(user, runner_id, flask.request.get_json())
            return ''

        @blueprint.route('/runners/<int:runner_id>', methods=['DELETE'])
        @authorize
        def runners_view_delete(user, runner_id: int):
            facade.delete(user, runner_id)
            return '', HTTPStatus.NO_CONTENT

        return blueprint
