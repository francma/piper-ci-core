from functools import wraps

import flask
from peewee import DoesNotExist

from piper_driver.models import User


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in flask.request.headers:
            flask.abort(401)

        user = None
        data = flask.request.headers['Authorization']
        token = str.replace(data, 'Bearer ', '')
        try:
            user = User.get(User.token == token)
        except DoesNotExist:
            flask.abort(403)
        return f(user=user, *args, **kwargs)
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

        return f(filters=query, order=order, limit=limit, offset=offset, *args, **kwargs)
    return decorated_function
