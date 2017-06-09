import uuid
from collections import namedtuple
import io
import pickle
import codecs

import pytest
from peewee import SqliteDatabase
from redis import Redis

from piper_driver.shell import PiperShell
from piper_driver.addins.common import Common
from piper_driver.addins.queue import Queue
from piper_driver.models import database_proxy
from piper_driver.models import models


def get_debug_db():
    database = SqliteDatabase(':memory:')
    database_proxy.initialize(database)
    database.create_tables(models)

    return database


@pytest.fixture()
def connection(monkeypatch):
    database = get_debug_db()
    monkeypatch.setattr('piper_driver.app.get_connection', lambda: database)
    monkeypatch.setattr('piper_driver.app.close_connection', lambda: None)
    yield database
    database.close()
    database = None


@pytest.fixture()
def redis():
    Common.REDIS_PREFIX = 'piper:test:' + uuid.uuid4().hex
    conn = Queue.connection = Redis()

    yield conn
    for key in conn.keys(Common.REDIS_PREFIX + '*'):
        conn.delete(key)


@pytest.fixture()
def shell(connection, monkeypatch):
    stdout = io.StringIO()
    user = namedtuple('User', ['email'])
    shell = PiperShell(user('email'), stdout=stdout)
    # monkeypatch.setattr('piper_driver.shell._print_list', lambda x: codecs.encode(pickle.dumps(x), "base64").decode())
    # monkeypatch.setattr('piper_driver.shell._format_get', lambda x: codecs.encode(pickle.dumps(x), "base64").decode())

    def read(pickled=False):
        output = stdout.getvalue()
        stdout.truncate(0)
        stdout.seek(0)
        if pickled:
            output = pickle.loads(codecs.decode(output.encode(), "base64"))

        return output

    yield read, shell

