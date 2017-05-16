from piper_driver.app import app
from piper_driver.models import *

app.testing = True


def test_authorize(connection):
    user1 = User.create(email='user1@email.com', role=UserRole.NORMAL)

    client = app.test_client()
    r = client.get('/build/1', headers={'Authorization': 'Bearer ' + user1.token})
    assert r.status_code == 200

