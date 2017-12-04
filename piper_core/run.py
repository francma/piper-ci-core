#!/usr/bin/env python3
import argparse
from pathlib import Path

import os
import uuid

import sys

import re
import yaml
from jsonschema import Draft4Validator, ValidationError

from piper_core.container import Container
from piper_core.model import models, User, UserRole
from piper_core.utils import authorized_keys

parser = argparse.ArgumentParser()
parser.add_argument(
    'config',
    help='Configuration file',
    type=Path
)
parser.add_argument(
    '--init',
    help='Initialize root user and exit',
    metavar='email public_key_path',
    type=str
)
parser.add_argument(
    '--reload',
    help='Configuration file',
    default=False,
    action='store_true',
)

parsed = vars(parser.parse_args())
config_path = parsed['config'].expanduser()
config = yaml.load(config_path.open())
cd = Path(__file__).parent.parent / 'openapi.yml'
with cd.open('r') as fp:
    schemas = yaml.load(fp)

schema = schemas['components']['schemas']['config']
try:
    Draft4Validator(schema=schema).validate(config)
except ValidationError as e:
    print('Invalid configuration file', file=sys.stderr)
    print(e.message, file=sys.stderr)
    exit(1)

container = Container(config)

init = parsed['init']
reload_keys = parsed['reload']

if init:
    container.init_db()
    connection = container.get_db()
    connection.create_tables(models)
    print('Database initialized')
    email, key = init.split()
    key_path = os.path.expanduser(key)
    with open(key_path) as fp:
        key = fp.read()

    key = (' '.join(key.split()[:2])).strip()

    user = {
        'role': str(UserRole.MASTER),
        'public_key': key,
        'email': email,
    }

    schema = schemas['components']['schemas']['user']
    try:
        Draft4Validator(schema=schema).validate(user)
    except ValidationError as e:
        print('Invalid user', file=sys.stderr)
        print(e.message, file=sys.stderr)
        exit(1)

    User.create(role=UserRole.MASTER, email=email, public_key=key)
    print('Created root user with email %s' % email)
    exit(0)

if reload_keys:
    authorized_keys_path = Path(config['app']['authorized_keys_path']).expanduser()
    authorized_keys.write(authorized_keys_path, config_path, User.select())
    print('Authorized keys file %s was updated' % authorized_keys_path)
    exit(0)

app = container.get_app()


def main() -> None:
    app.run()


if __name__ == '__main__':
    main()
