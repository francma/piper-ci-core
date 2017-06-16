#!/usr/bin/env python3
import os

import flask
import click
from peewee import MySQLDatabase
from playhouse import db_url

from piper_driver.views import piper_views
from piper_driver.models import *
from piper_driver.addins import authorized_keys

app = flask.Flask(__name__)

app.config['DATABASE'] = 'mysql://root:chleba11@localhost:3306/piper_driver'
app.config['SECRET_KEY'] = 'SECRET'
app.config['AUTHORIZED_KEYS_PATH'] = os.path.expanduser('~/.ssh/authorized_keys')


def get_connection():
    connection = db_url.connect(app.config['DATABASE'])
    database_proxy.initialize(connection)

    return connection


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
    nargs=2,
    type=str,
    metavar='[root_email] [public_key_file]',
    help='Create database tables, create ROOT user and exit.'
)
@click.option(
    '--reload-keys',
    is_flag=True,
    help='Force reload user public keys and exit',
)
@click.option(
    '--database',
    type=str,
    metavar='[scheme]://[user]:[password]@[host]:[port]/[database]'
)
def main(init, reload_keys: bool, database: str):
    app.config['DATABASE'] = database
    connection = get_connection()

    if init:
        connection.create_tables(models)
        print('Database initialized')
        email, key = init
        key_path = os.path.expanduser(key)
        with open(key_path) as fp:
            key = fp.read()
        User.create(role=UserRole.MASTER, email=email, public_key=key)
        print('Created root user with email %s' % email)
        exit(0)
    if reload_keys:
        authorized_keys.write(app.config['AUTHORIZED_KEYS_PATH'], User.select())
        print('Authorized keys file %s was updated' % app.config['AUTHORIZED_KEYS_PATH'])
        exit(0)

    app.run(port=5001)

if __name__ == '__main__':
    main()
