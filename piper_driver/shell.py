#!/usr/bin/env python3
import cmd
import sys
import shlex
import os

from flask_jwt_extended import create_access_token
from peewee import MySQLDatabase
from peewee import SqliteDatabase

from piper_driver.app import app
from piper_driver.models.entities import database_proxy
from piper_driver.models.entities import tables
from piper_driver.models.entities import User
from piper_driver.models.entities import UserRole
from piper_driver.repository.identity import IdentityRepository


class PiperShell(cmd.Cmd):

    def __init__(self, user: User):
        super(PiperShell, self).__init__()
        self._user = user
        self.prompt = user.username + '> '
        self._identity = IdentityRepository()

    def _dict2str(self, d):
        r = ['{}: {}'.format(k, v) for k, v in d.items()]
        r = os.linesep.join(r)
        return r

    def do_token(self, args):
        with app.app_context():
            jwt_token = create_access_token(identity=user_id)
            print(jwt_token)

    def do_user(self, args: str):
        args = shlex.split(args)

        if args[0] not in ['set', 'get', 'create']:
            print('ERR')
            return

    def do_self(self, args: str):
        args = shlex.split(args)
        if len(args) == 0:
            result = self._identity.get(self._user)
            print(self._dict2str(result))
            return

        action = args[0]
        if action not in ['set', 'get']:
            print('ERR')
            return

        if action == 'get':
            properties = args[1:]
            if len(properties) == 0:
                properties = None
            result = self._identity.get(self._user, properties)
            if len(result) == 1:
                print(list(result.values())[0])
                return

            print(self._dict2str(result))
            return

        if action == 'set':
            properties = args[1:]
            if len(properties) % 2 != 0 or len(properties) == 0:
                print('ERR')
                return

            properties = dict(zip(properties[::2], properties[1::2]))
            self._identity.update(properties, self._user)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Expecting exactly 1 argument (userId)', file=sys.stderr)
        exit(1)

    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print('First argument should be integer', file=sys.stderr)
        exit(1)

    database = SqliteDatabase(':memory:')
    database_proxy.initialize(database)
    database.create_tables(tables)
    user_root = User.create(username='root', password='password', role=UserRole.ROOT, email='me@martinfranc.eu')

    shell = PiperShell(user_root)

    shell.cmdloop()


