import flask
from http import HTTPStatus

from piper_core.blueprints.helpers import authorize, query_parse
from piper_core.model import *


class UserBlueprintFactory:

    @staticmethod
    def create(facade: UsersFacade):
        blueprint = flask.Blueprint('user', __name__)

        @blueprint.route('/users/<int:user_id>', methods=['GET'])
        @authorize
        def users_view_get(user, user_id: int):
            return flask.jsonify(facade.get(user, user_id))

        @blueprint.route('/users', methods=['GET'])
        @query_parse
        @authorize
        def users_view_list(filters, order, limit, offset, user):
            return flask.jsonify(facade.list(user, filters, order, limit, offset))

        @blueprint.route('/users/count', methods=['GET'])
        @authorize
        def users_view_count(user):
            filters = flask.request.args.items()
            count = facade.count(user, filters)

            return flask.jsonify({'count': count})

        @blueprint.route('/users', methods=['POST'])
        @authorize
        def users_view_create(user):
            facade.create(user, flask.request.get_json())
            return '', HTTPStatus.CREATED

        @blueprint.route('/users/<int:user_id>', methods=['POST'])
        @authorize
        def users_view_update(user, user_id: int):
            facade.update(user, user_id, flask.request.get_json())
            return ''

        @blueprint.route('/users/<int:user_id>', methods=['DELETE'])
        @authorize
        def users_view_delete(user, user_id: int):
            facade.delete(user, user_id)
            return '', HTTPStatus.NO_CONTENT

        return blueprint
