import flask

from piper_core.utils.github import WebhookParseException
from piper_core.model import *


class WebhookBlueprintFactory:

    @staticmethod
    def create(builds_facade: BuildsFacade):
        blueprint = flask.Blueprint('webhook', __name__)

        @blueprint.route('/webhook', methods=['POST'])
        def webhook():
            data = flask.request.get_json()

            try:
                builds_facade.parse_webhook(data)
            except WebhookParseException:
                return '', 400

            return ''

        return blueprint
