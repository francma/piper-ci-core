import flask
from http import HTTPStatus

from piper_core.blueprints.helpers import authorize, query_parse
from piper_core.model import *


class ProjectBlueprintFactory:

    @staticmethod
    def create(facade: ProjectsFacade):
        blueprint = flask.Blueprint('projects', __name__)

        @blueprint.route('/projects/<int:project_id>', methods=['GET'])
        @authorize
        def projects_view_get(user, project_id: int):
            return flask.jsonify(facade.get(user, project_id))

        @blueprint.route('/projects', methods=['GET'])
        @query_parse
        @authorize
        def projects_view_list(filters, order, limit, offset, user):
            return flask.jsonify(facade.list(user, filters, order, limit, offset))

        @blueprint.route('/projects/count', methods=['GET'])
        @authorize
        def projects_view_count(user):
            filters = flask.request.args.items()
            count = facade.count(user, filters)

            return flask.jsonify({'count': count})

        @blueprint.route('/projects', methods=['POST'])
        @authorize
        def projects_view_create(user):
            facade.create(user, flask.request.get_json())
            return '', HTTPStatus.CREATED

        @blueprint.route('/projects/<int:project_id>', methods=['PUT'])
        @authorize
        def projects_view_update(user, project_id: int):
            facade.update(user, project_id, flask.request.get_json())
            return ''

        @blueprint.route('/projects/<int:project_id>', methods=['DELETE'])
        @authorize
        def projects_view_delete(user, project_id: int):
            facade.delete(user, project_id)
            return '', HTTPStatus.NO_CONTENT

        @blueprint.route('/projects/<int:project_id>/users', methods=['GET'])
        @authorize
        def projects_view_get_users(user, project_id: int):
            return flask.jsonify(facade.user_list(user, project_id))

        @blueprint.route('/projects/<int:project_id>/users', methods=['PUT'])
        @authorize
        def projects_view_add_user(user, project_id: int):
            json = flask.request.json
            json['project_id'] = project_id
            facade.user_add(user, json)
            return '', HTTPStatus.CREATED

        @blueprint.route('/projects/<int:project_id>/users/<int:user_id>', methods=['DELETE'])
        @authorize
        def projects_view_delete_user(user, project_id: int, user_id: int):
            facade.user_remove(user, {'project_id': project_id, 'user_id': user_id})
            return '', HTTPStatus.NO_CONTENT

        return blueprint
