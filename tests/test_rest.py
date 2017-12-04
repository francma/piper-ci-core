from http import HTTPStatus

from piper_core.model import *
from piper_core.container import Container


def test_authorize(container: Container):
    app = container.get_app()
    app.testing = True

    user1 = User.create(email='user1@email.com', role=UserRole.NORMAL, public_key='AAA')

    client = app.test_client()
    r = client.get('/identity', headers={'Authorization': 'Bearer ' + str(user1.token)})
    assert r.status_code is not HTTPStatus.FORBIDDEN
