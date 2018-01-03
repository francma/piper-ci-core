from typing import Dict, Any

import flask


class HomepageBlueprintFactory:

    @staticmethod
    def create(schema: Dict[Any, Any]):
        homepage_view = flask.Blueprint('homepage_view', __name__)

        @homepage_view.route('/', methods=['GET'])
        def homepage_view_get():
            return flask.jsonify(schema)

        return homepage_view
