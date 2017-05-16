#!/usr/bin/env python3
import cmd
import sys
import shlex
import functools
from enum import Enum

from peewee import MySQLDatabase
from peewee import SqliteDatabase

from piper_driver.models import *
from piper_driver.repository import *


class Action(Enum):
    GET = 1
    LIST = 2
    DELETE = 3
    UPDATE = 4
    CREATE = 5
    RESTART = 6

_actions = {
    '': Action.LIST,
    'list': Action.LIST,
    'get': Action.GET,
    'delete': Action.DELETE,
    'set': Action.UPDATE,
    'create': Action.CREATE,
    'restart': Action.RESTART,
}


def _parse(mapping=None):
    if mapping is not None:
        mapping = {**_actions, **mapping}
    else:
        mapping = _actions

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, args):
            args = shlex.split(args)
            if len(args) == 0:
                args = ['']

            action = mapping[args[0]]
            del args[0]

            return func(self, action, args)
        return wrapper
    return decorator


class PiperShell(cmd.Cmd):

    def __init__(self, user: User):
        super().__init__()
        self._user = user
        self.prompt = user.email + '> '
        self._repositories = {
            'identity': IdentityRepository,
            'build': BuildRepository,
            'project': ProjectRepository,
            'job': JobRepository,
        }

    def onecmd(self, line):
        try:
            super().onecmd(line)
        except RepositoryPermissionDenied:
            print('Permission denied')
        except RepositoryNotFound:
            print('Not found')
        except RepositoryNotImplementedException:
            print('Not supported')

    @_parse(mapping={'': Action.GET})
    def do_identity(self, action, args):
        if action is Action.GET:
            print(self._repositories['identity'].get(None, self._user))
            return
        if action is Action.UPDATE:
            self._repositories['identity'].update(None, self._parse_pairs(args), self._user)
            self.prompt = self._user.email + '> '
            return

    @_parse()
    def do_build(self, action, args):
        self._do('build', action, args)

    @_parse()
    def do_project(self, action, args):
        self._do('project', action, args)

    @_parse()
    def do_job(self, action, args):
        self._do('job', action, args)

    def _do(self, repo, action, args):
        if action is Action.GET:
            idx = args[0] if len(args) else 0
            print(self._repositories[repo].get(idx, self._user))
            return
        if action is Action.LIST:
            _args = self._parse_list(args)
            _args['user'] = self._user
            print(self._repositories[repo].list(**_args))
            return
        if action is Action.CREATE:
            self._repositories[repo].create(self._parse_pairs(args), self._user)
            return
        if action is Action.UPDATE:
            idx = args[0] if len(args) else 0
            if len(args):
                del args[0]
            self._repositories[repo].update(idx, self._parse_pairs(args), self._user)
            return

    def _parse_pairs(self, args):
        return dict(zip(args[::2], args[1::2]))

    def _parse_list(self, args):
        pairs = self._parse_pairs(args)

        if 'limit' not in pairs:
            limit = 10
        else:
            del pairs['limit']

        if 'offset' not in pairs:
            offset = 0
        else:
            del pairs['offset']

        if 'order' not in pairs:
            order = list()
        else:
            order = pairs['order'].split(',')
            del pairs['order']

        if 'master' not in pairs:
            master = False
        else:
            master = True
            del pairs['master']

        result = {
            'limit': limit,
            'offset': offset,
            'order': order,
            'master': master,
            'filters': pairs,
        }

        return result


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
    database.create_tables(models)
    user_root = User.create(role=UserRole.MASTER, email='me@martinfranc.eu')

    shell = PiperShell(user=user_root)
    shell.cmdloop()


