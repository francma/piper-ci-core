import tempfile

from collections import namedtuple
import io
import pickle
import codecs

import pytest
from peewee import SqliteDatabase

from piper_core.container import Container
from piper_core.model import database_proxy, models
from piper_core.shell import PiperShell


def get_debug_db():
    database = SqliteDatabase(':memory:')
    database_proxy.initialize(database)
    database.create_tables(models)

    return database


@pytest.fixture()
def container(monkeypatch):
    database = get_debug_db()
    monkeypatch.setattr('piper_core.container.Container.get_db', lambda x: database)

    with tempfile.TemporaryDirectory() as tempdir:
        c = Container({
            'app': {
                'secret': 'abc',
                'authorized_keys_path': 'a',
                'port': 6000,
                'job_log_dir': tempdir,
            },
            'queue': {
                'backend': 'redis',
                'url': 'redis://@localhost:6379/12'
            },
        })

        c.init_db()
        yield c
        c.get_queue().connection.flushdb()


@pytest.fixture()
def shell(container: Container, monkeypatch):
    stdout = io.StringIO()
    user = namedtuple('User', ['email'])

    monkeypatch.setattr(PiperShell, '_confirm_yes', lambda x: True)
    piper = container.get_shell(user('email'))
    piper.stdout = stdout
    piper.SLEEP_DURATION = 0

    def read(pickled=False):
        output = stdout.getvalue()
        stdout.truncate(0)
        stdout.seek(0)
        if pickled:
            output = pickle.loads(codecs.decode(output.encode(), 'base64'))

        return output

    yield read, piper
