#!/usr/bin/env python3
import cmd
import sys
from configparser import ConfigParser
import re

from texttable import Texttable
import click

from piper_driver import app
from piper_driver.models import *
from piper_driver.repository import *
from piper_driver.addins.exceptions import *


class PiperShell(cmd.Cmd):

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    @property
    def prompt(self) -> str:
        return self.user.email + '> '

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except ShellException as e:
            print(e, file=self.stdout)
        except RepositoryPermissionDenied:
            print('Permission denied', file=self.stdout)
        except RepositoryNotFound:
            print('Not found', file=self.stdout)

    def postcmd(self, stop, line):
        if stop:
            raise SystemExit

    def do_exit(self, args):
        print('Bye!', file=self.stdout)
        return True

    def _parse_args(self, args: str):
        args = '[root]\n' + args
        args = re.sub(r'\s*(\w+)\s*=', r'\n\1=', args)
        config = ConfigParser()
        config.read_string(args)
        args = dict(config.items('root'))

        return args

    def _parse_list(self, args):
        kwargs = self._parse_args(args)
        actual = dict()
        actual['limit'] = kwargs['limit'] if 'limit' in kwargs else 10
        actual['offset'] = kwargs['offset'] if 'offset' in kwargs else 0
        actual['order'] = kwargs['order'].split(',') if 'order' in kwargs else None
        actual['filters'] = kwargs

        return actual

    def _pop_id(self, args: str):
        pos = args.find(' ')
        if pos == -1:
            idx, args = args, ''
        else:
            idx, args = args[:pos], args[pos:]

        return int(idx), args

    def route(self, do, args):
        action, *args = args.split(' ', 1)
        args = ''.join(args)
        fn = do + '_' + action.replace('-', '_')
        if hasattr(self, fn):
            getattr(self, fn)(args)
        else:
            raise ShellException('Subcommand does not exist')

    def do_identity(self, args):
        self.route('identity', args)

    def identity_get(self, args):
        print(IdentityRepository.get(self.user, None), file=self.stdout)

    def identity_update(self, args):
        IdentityRepository.update(self.user, None, self._parse_args(args))
        self.user = User.get(User.id == self.user.id)
        print('Updated identity', file=self.stdout)

    def do_project(self, args):
        self.route('project', args)

    def project_get(self, args):
        idx, args = self._pop_id(args)
        item = ProjectRepository.get(self.user, idx)
        print(item, file=self.stdout)

    def project_list(self, args):
        print(ProjectRepository.list(self.user, **self._parse_list(args)), file=self.stdout)

    def project_count(self, args):
        print(ProjectRepository.count(self.user, self._parse_args(args)), file=self.stdout)

    def project_create(self, args):
        idx = ProjectRepository.create(self.user, self._parse_args(args))
        print('Created new project with id = %d' % idx, file=self.stdout)

    def project_update(self, args):
        idx, args = self._pop_id(args)
        ProjectRepository.update(self.user, idx, self._parse_args(args))
        print('Updated project with id = %d' % idx, file=self.stdout)

    def project_delete(self, args):
        idx, args = self._pop_id(args)
        ProjectRepository.delete(self.user, idx)
        print('Deleted project with id = %d' % idx, file=self.stdout)

    def project_user_list(self, args):
        result = ProjectRepository.user_list(self.user, **self._parse_list(args))
        print(result, file=self.stdout)

    def project_user_add(self, args):
        ProjectRepository.user_add(self.user, self._parse_args(args))

    def project_user_remove(self, args):
        ProjectRepository.user_remove(self.user, self._parse_args(args))

    def do_build(self, args):
        self.route('build', args)

    def build_get(self, args):
        idx, args = self._pop_id(args)
        item = BuildsRepository.get(self.user, idx)
        print(item, file=self.stdout)

    def build_list(self, args):
        result = BuildsRepository.user_list(self.user, **self._parse_list(args))
        print(result, file=self.stdout)

    def build_count(self, args):
        print(ProjectRepository.count(self.user, self._parse_args(args)))

    def build_cancel(self, args):
        idx, args = self._pop_id(args)
        BuildsRepository.cancel(self.user, idx)
        print('Canceled', file=self.stdout)

    def build_restart(self, args):
        idx, args = self._pop_id(args)
        BuildsRepository.restart(self.user, idx)
        print('Restarted', file=self.stdout)

    def do_stage(self, args):
        self.route('stage', args)

    def stage_get(self, args):
        idx, args = self._pop_id(args)
        item = StagesRepository.get(self.user, idx)
        print(item, file=self.stdout)

    def stage_list(self, args):
        result = StagesRepository.user_list(self.user, **self._parse_list(args))
        print(result, file=self.stdout)

    def stage_count(self, args):
        print(StagesRepository.count(self.user, self._parse_args(args)))

    def stage_cancel(self, args):
        idx, args = self._pop_id(args)
        StagesRepository.cancel(self.user, idx)
        print('Canceled', file=self.stdout)

    def stage_restart(self, args):
        idx, args = self._pop_id(args)
        StagesRepository.restart(self.user, idx)
        print('Restarted', file=self.stdout)

    def do_job(self, args):
        self.route('job', args)

    def job_get(self, args):
        idx, args = self._pop_id(args)
        item = JobRepository.get(self.user, idx)
        print(item, file=self.stdout)

    def job_list(self, args):
        result = JobRepository.user_list(self.user, **self._parse_list(args))
        print(result, file=self.stdout)

    def job_count(self, args):
        print(JobRepository.count(self.user, self._parse_args(args)))

    def job_cancel(self, args):
        idx, args = self._pop_id(args)
        JobRepository.cancel(self.user, idx)
        print('Canceled', file=self.stdout)

    def job_restart(self, args):
        idx, args = self._pop_id(args)
        StagesRepository.restart(self.user, idx)
        print('Canceled', file=self.stdout)

    def do_user(self, args):
        self.route('user', args)

    def user_get(self, args):
        idx, args = self._pop_id(args)
        item = UsersRepository.get(self.user, idx)
        print(item, file=self.stdout)

    def user_list(self, args):
        result = UsersRepository.list(self.user, **self._parse_list(args))
        print(result, file=self.stdout)

    def user_count(self, args):
        print(UsersRepository.count(self.user, self._parse_args(args)))

    def user_create(self, args):
        idx = UsersRepository.create(self.user, self._parse_args(args))
        print('Created new user with id = %d' % idx, file=self.stdout)

    def user_update(self, args):
        idx, args = self._pop_id(args)
        UsersRepository.update(self.user, idx, self._parse_args(args))
        print('Updated user with id = %d' % idx, file=self.stdout)

    def user_delete(self, args):
        idx, args = self._pop_id(args)
        UsersRepository.delete(self.user, idx)
        print('Deleted user with id = %d' % idx, file=self.stdout)

    def do_runner(self, args):
        self.route('runner', args)

    def runner_get(self, args):
        idx, args = self._pop_id(args)
        item = RunnerRepository.get(self.user, idx)
        print(item, file=self.stdout)

    def runner_list(self, args):
        result = RunnerRepository.list(self.user, **self._parse_list(args))
        print(result, file=self.stdout)

    def runner_count(self, args):
        print(RunnerRepository.count(self.user, self._parse_args(args)))

    def runner_create(self, args):
        idx = RunnerRepository.create(self.user, self._parse_args(args))
        print('Created new runner with id = %d' % idx, file=self.stdout)

    def runner_update(self, args):
        idx, args = self._pop_id(args)
        RunnerRepository.update(self.user, idx, self._parse_args(args))
        print('Updated user with id = %d' % idx, file=self.stdout)

    def runner_delete(self, args):
        idx, args = self._pop_id(args)
        RunnerRepository.delete(self.user, idx)
        print('Deleted runner with id = %d' % idx, file=self.stdout)


# def _print_list(result):
#     table = Texttable()
#     table.add_rows([result[0].keys(), *[x.values() for x in result]])
#     return table.draw()

@click.command()
@click.argument(
    'user_id',
    nargs=1,
    type=int,
)
def main(user_id):
    database = app.get_connection()
    logged_user = User.get(User.id == user_id)

    PiperShell(user=logged_user).cmdloop()


if __name__ == '__main__':
    main()




