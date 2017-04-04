from flask_restful import Resource, abort
from flask_restful import reqparse
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from piper_driver.models.entities import User
from piper_driver.repository.identity import IdentityRepository


class IdentityPresenterList(Resource):

    def __init__(self):
        super(IdentityPresenterList, self).__init__()
        self._identity = IdentityRepository

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = User.get(User.id == user_id)
        result = self._identity.get(user)

        return result

    @jwt_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, location='json')
        parser.add_argument('role', type=str, location='json')
        args = parser.parse_args()

        user_id = get_jwt_identity()
        user = User.get(User.id == user_id)
        self._identity.update(args, user)
