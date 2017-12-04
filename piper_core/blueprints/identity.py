import flask

from piper_core.blueprints.helpers import authorize
from piper_core.model import *


class IdentityBlueprintFactory:

    @staticmethod
    def create(facade: UsersFacade):
        blueprint = flask.Blueprint('identity', __name__)

        @blueprint.route('/identity', methods=['GET'])
        @authorize
        def jobs_view_list(user):
            return flask.jsonify(facade.get(user, user.id))

        return blueprint
