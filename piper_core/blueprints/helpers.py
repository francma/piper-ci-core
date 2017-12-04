from functools import wraps
from http import HTTPStatus

import flask
from peewee import DoesNotExist

from piper_core.model import *


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in flask.request.headers:
            user = User()
            user.role = UserRole.GUEST
            user.email = 'guest@piper'
            user.token = ''

            return f(user=user, *args, **kwargs)

        data = flask.request.headers['Authorization']
        token = str.replace(data, 'Bearer ', '')
        try:
            user = User.get(User.token == token)
            return f(user=user, *args, **kwargs)
        except DoesNotExist:
            flask.abort(HTTPStatus.UNAUTHORIZED)
    return decorated_function


def query_parse(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        query = flask.request.args.items()
        if 'limit' in query:
            limit = query['limit']
            del query['limit']
        else:
            limit = 10

        if 'offset' in query:
            offset = query['offset']
            del query['offset']
        else:
            offset = 0

        if 'order' in query:
            order = query['order'].split(',')
            del query['order']
        else:
            order = []

        return f(filters=dict(query), order=order, limit=limit, offset=offset, *args, **kwargs)
    return decorated_function
