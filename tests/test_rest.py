from http import HTTPStatus

from piper_driver.app import app
from piper_driver.models import *

app.testing = True


def test_authorize(connection):
    user1 = User.create(email='user1@email.com', role=UserRole.NORMAL)

    client = app.test_client()
    r = client.get('/projects', headers={'Authorization': 'Bearer ' + str(user1.token)})
    assert r.status_code is not HTTPStatus.FORBIDDEN

