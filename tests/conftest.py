import uuid

import pytest
from peewee import SqliteDatabase
from redis import Redis

from piper_driver.addins.common import Common
from piper_driver.addins.queue import Queue
from piper_driver.models import database_proxy
from piper_driver.models import models


@pytest.fixture()
def connection():
    database = SqliteDatabase(':memory:')
    database_proxy.initialize(database)
    database.create_tables(models)

    yield database


@pytest.fixture()
def redis():
    Common.REDIS_PREFIX = 'piper:test:' + uuid.uuid4().hex
    conn = Queue.connection = Redis()

    yield conn
    for key in conn.keys(Common.REDIS_PREFIX + '*'):
        conn.delete(key)
