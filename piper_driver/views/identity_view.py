import flask

from piper_driver.views.helpers import authorize
from piper_driver.repository import IdentityRepository

identity_view = flask.Blueprint('identity_view', __name__)


@identity_view.route('/identity', methods=['GET'])
@authorize
def jobs_view_list(user):
    return flask.jsonify(IdentityRepository.get(user, None))
