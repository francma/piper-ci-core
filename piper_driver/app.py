#!/usr/bin/env python3
import os

import flask
import click
from peewee import MySQLDatabase

from piper_driver.views import piper_views
from piper_driver.models import *
from piper_driver.addins import authorized_keys

app = flask.Flask(__name__)

app.config['DATABASE_NAME'] = 'piper_driver'
app.config['DATABASE_USER'] = 'root'
app.config['DATABASE_PASSWORD'] = 'chleba11'
app.config['SECRET_KEY'] = 'SECRET'
app.config['AUTHORIZED_KEYS_PATH'] = os.path.expanduser('~/.ssh/authorized_keys')


def get_connection():
    database = MySQLDatabase(
        app.config['DATABASE_NAME'],
        user=app.config['DATABASE_USER'],
        password=app.config['DATABASE_PASSWORD']
    )
    database_proxy.initialize(database)

    return database


def close_connection():
    if not database_proxy.is_closed():
        database_proxy.close()


@app.before_request
def connect():
    get_connection()


@app.after_request
def disconnect(response):
    close_connection()

    return response

for view in piper_views:
    app.register_blueprint(view)


@app.route('/')
def hello():
    return 'Hello!\n'


@click.command()
@click.option(
    '--init',
    is_flag=True,
)
@click.option(
    '--reload-keys',
    is_flag=True,
)
def main(init: bool, reload_keys: bool):
    if init:
        database = get_connection()
        database_proxy.initialize(database)
        database.create_tables(models)
        print('Database initialized')
        exit(0)
    if reload_keys:
        database = get_connection()
        database_proxy.initialize(database)
        authorized_keys.write(app.config['AUTHORIZED_KEYS_PATH'], User.select())
        print('Authorized keys file %s was updated' % app.config['AUTHORIZED_KEYS_PATH'])
        exit(0)

    app.run()

if __name__ == '__main__':
    main()
