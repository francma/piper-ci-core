#!/usr/bin/env python3
import argparse
import cmd
import time
from configparser import ConfigParser, ParsingError
from pathlib import Path
from typing import Dict, Any

import re

import yaml

from piper_core.model import *
from piper_core.utils.exceptions import *


class PiperShell(cmd.Cmd):

    SLEEP_DURATION = 1

    def __init__(self, user: User, users_facade: UsersFacade, builds_facade: BuildsFacade, jobs_facade: JobsFacade,
                 projects_facade: ProjectsFacade, runners_facade: RunnersFacade, stages_facade: StagesFacade) -> None:
        super().__init__()
        self.stages_facade = stages_facade
        self.runners_facade = runners_facade
        self.projects_facade = projects_facade
        self.jobs_facade = jobs_facade
        self.builds_facade = builds_facade
        self.users_facade = users_facade
        self.user = user
        self.prompt = '[%s]$ ' % self.user.email

    def pretty_print(self, item):
        yaml.dump(item, self.stdout, default_flow_style=False)

    def onecmd(self, line):
        try:
            return super().onecmd(line)
        except ShellException as e:
            print('Shell ERROR')
            print(e, file=self.stdout)
        except FacadeException as e:
            print('Facade ERROR')
            print(str(e), file=self.stdout)
        except ParsingError:
            print('Parse ERROR')
            print('Invalid command line arguments', file=self.stdout)

    def postcmd(self, stop, line):
        if stop:
            raise SystemExit

    def do_exit(self, args):
        """Exits shell"""
        if args:
            raise ShellException('This command have no arguments')

        print('Bye!', file=self.stdout)
        return True

    def _parse_args(self, args: str):
        args = '[root]\n' + args
        args = re.sub(r'\s*(\w+)\s*=', r'\n\1=', args)
        config = ConfigParser()
        config.read_string(args)
        items: Dict[str, Any] = dict(config.items('root'))

        # guess types
        for k, v in items.items():
            if v[0] == '"' and v[-1] == '"':
                items[k] = v[1:-1]
                continue
            try:
                items[k] = int(v)
            except ValueError:
                pass

        return items

    def _parse_list(self, args):
        kwargs = self._parse_args(args)
        actual = dict()
        actual['limit'] = kwargs['limit'] if 'limit' in kwargs else 10
        actual['offset'] = kwargs['offset'] if 'offset' in kwargs else 0
        actual['order'] = kwargs['order'].split(',') if 'order' in kwargs else None
        actual['filters'] = kwargs

        return actual

    def _confirm_yes(self, message='Are you sure? [Y/n]'):
        yes = {'yes', 'y', 'ye', ''}

        choice = input(message).lower()
        if choice in yes:
            return True
        else:
            return False

    def _pop_id(self, args: str):
        pos = args.find(' ')
        if pos == -1:
            idx, args = args, ''
        else:
            idx, args = args[:pos], args[pos:]

        try:
            return int(idx), args
        except ValueError:
            raise ShellException('Value "%s" is not a an integer' % idx)

    def route(self, do, args):
        action, *args = args.split(' ', 1)
        args = ''.join(args)
        fn = do + '_' + action.replace('-', '_')
        if hasattr(self, fn):
            getattr(self, fn)(args)
        else:
            raise ShellException('Sub-command does not exist')

    def do_identity(self, args):
        """
> identity get
> identity update [email = str] [role = (master, admin, normal)] [token = str] [public_key = str]
        """
        self.route('identity', args)

    def identity_get(self, args):
        if args:
            raise ShellException('This command have no arguments')

        self.pretty_print(self.users_facade.get(self.user, self.user.id))

    def identity_update(self, args):
        args = self._parse_args(args)
        user = self.users_facade.get(self.user, self.user.id)
        args = {**user, **args}

        self.pretty_print(args)
        if self._confirm_yes():
            self.users_facade.update(self.user, self.user.id, args)
            self.user = User.get(User.id == self.user.id)
            print('User updated', file=self.stdout)
        else:
            print('Nothing happened', file=self.stdout)

    def do_project(self, args):
        """
> project get [project_id]
> project list [url = str] [origin = str]
  [limit = int] [offset = int] [order = (created-desc|created-asc)]
> project count [url = str] [origin = str]
> project update [project_id] [url = str] [origin = str]
> project create [url = str] [origin = str]
        """
        self.route('project', args)

    def project_get(self, args):
        idx, args = self._pop_id(args)
        item = self.projects_facade.get(self.user, idx)
        self.pretty_print(item)

    def project_list(self, args):
        self.pretty_print(self.projects_facade.list(self.user, **self._parse_list(args)))

    def project_count(self, args):
        print(self.projects_facade.count(self.user, self._parse_args(args)), file=self.stdout)

    def project_create(self, args):
        idx = self.projects_facade.create(self.user, self._parse_args(args))
        print('Created new project with id = %d' % idx, file=self.stdout)

    def project_update(self, args):
        idx, args = self._pop_id(args)
        args = self._parse_args(args)
        project = self.projects_facade.get(self.user, idx)
        del project['id'], project['status']
        args = {**project, **args}

        self.pretty_print(args)
        if self._confirm_yes():
            self.projects_facade.update(self.user, idx, args)
            print('Project updated', file=self.stdout)
        else:
            print('Nothing happened', file=self.stdout)

    def project_delete(self, args):
        idx, args = self._pop_id(args)
        if self._confirm_yes():
            self.projects_facade.delete(self.user, idx)
            print('Deleted project with id = %d' % idx, file=self.stdout)
        else:
            print('Nothing happened', file=self.stdout)

    def project_user_list(self, args):
        idx, args = self._pop_id(args)
        result = self.projects_facade.user_list(self.user, idx)
        self.pretty_print(result)

    def project_user_add(self, args):
        args = self._parse_args(args)
        if self._confirm_yes():
            self.projects_facade.user_add(self.user, args)
            print('Added user to project', file=self.stdout)
        else:
            print('Nothing happened', file=self.stdout)

    def project_user_remove(self, args):
        args = self._parse_args(args)
        if self._confirm_yes():
            self.projects_facade.user_remove(self.user, args)
            print('Removed user from project', file=self.stdout)
        else:
            print('Nothing happened', file=self.stdout)

    def do_build(self, args):
        """
> build get [build_id]
> build list [project_id = int] [branch = str]
  [status = (created|ready|pending|running|failed|success|canceled|skipped|error)]
  [limit = int] [offset = int] [order = (created-desc|created-asc)]
> build count [project_id = int] [branch = str] [status = ()]
  [limit = int] [offset = int] [order = (created-desc|created-asc)]
> build cancel [build_id]
> build restart [build_id]
        """
        self.route('build', args)

    def build_get(self, args):
        idx, args = self._pop_id(args)
        item = self.builds_facade.get(self.user, idx)
        self.pretty_print(item)

    def build_list(self, args):
        result = self.builds_facade.list(self.user, **self._parse_list(args))
        self.pretty_print(result)

    def build_count(self, args):
        print(self.builds_facade.count(self.user, self._parse_args(args)))

    def build_cancel(self, args):
        idx, args = self._pop_id(args)
        if self._confirm_yes():
            self.builds_facade.cancel(self.user, idx)
            print('Canceled', file=self.stdout)
        else:
            print('Nothing happened')

    def build_restart(self, args):
        idx, args = self._pop_id(args)
        if self._confirm_yes():
            self.builds_facade.restart(self.user, idx)
            print('Restarted', file=self.stdout)
        else:
            print('Nothing happened')

    def do_stage(self, args):
        """
> stage get [stage_id]
> stage list [project_id = int] [build_id = int]
  [status = (created|ready|pending|running|failed|success|canceled|skipped|error)]
  [limit = int] [offset = int]
> stage count
  [project_id = int] [build_id = int]
  [status = (created|ready|pending|running|failed|success|canceled|skipped|error)]
> stage cancel [stage_id]
> stage restart [stage_id]
        """
        self.route('stage', args)

    def stage_get(self, args):
        idx, args = self._pop_id(args)
        item = self.stages_facade.get(self.user, idx)
        self.pretty_print(item)

    def stage_list(self, args):
        result = self.stages_facade.list(self.user, **self._parse_list(args))
        self.pretty_print(result)

    def stage_count(self, args):
        print(self.stages_facade.count(self.user, self._parse_args(args)))

    def stage_cancel(self, args):
        idx, args = self._pop_id(args)
        if self._confirm_yes():
            self.stages_facade.cancel(self.user, idx)
            print('Canceled', file=self.stdout)
        else:
            print('Nothing happened')

    def stage_restart(self, args):
        idx, args = self._pop_id(args)
        if self._confirm_yes():
            self.stages_facade.cancel(self.user, idx)
            print('Restarted', file=self.stdout)
        else:
            print('Nothing happened')

    def do_job(self, args):
        """
> job get [job_id]
> job list
  [project_id = int] [build_id = int] [stage_id = int]
  [status = (created|ready|pending|running|failed|success|canceled|skipped|error)]
  [limit = int] [offset = int]
> job count
  [project_id = int] [build_id = int] [stage_id = int]
  [status = (created|ready|pending|running|failed|success|canceled|skipped|error)]
> job cancel [job_id]
> job restart [job_id]
> job log [job_id]
        """
        self.route('job', args)

    def job_get(self, args):
        idx, args = self._pop_id(args)
        item = self.jobs_facade.get(self.user, idx)
        self.pretty_print(item)

    def job_list(self, args):
        result = self.jobs_facade.list(self.user, **self._parse_list(args))
        self.pretty_print(result)

    def job_count(self, args):
        print(self.jobs_facade.count(self.user, self._parse_args(args)))

    def job_cancel(self, args):
        idx, args = self._pop_id(args)
        if self._confirm_yes():
            self.jobs_facade.cancel(self.user, idx)
            print('Canceled', file=self.stdout)
        else:
            print('Nothing happened')

    def job_restart(self, args):
        idx, args = self._pop_id(args)
        if self._confirm_yes():
            self.jobs_facade.restart(self.user, idx)
            print('Restarted', file=self.stdout)
        else:
            print('Nothing happened')

    # whole log
    def job_log(self, args):
        idx, args = self._pop_id(args)
        job: Job = Job.get(Job.id == idx)
        start_regex = re.compile(r'^::piper:(command|after_failure):(\d+):start:(\d+)::$', re.MULTILINE)
        end_regex = re.compile(r'^::piper:(command|after_failure):(\d+):end:(\d+):(\d+)::$', re.MULTILINE)
        offset = 0

        def start_fn(match) -> str:
            typex, order = match.group(1), int(match.group(2))

            if typex == 'command':
                return '$ ' + job.commands[order].cmd
            elif typex == 'after_failure':
                return '$ ' + job.after_failure[order].cmd
            else:
                raise Exception

        def end_fn(match) -> str:
            # typex, order, timestamp, exit_code = match.group(1), int(match.group(2)), int(match.group(3)),\
            #                                      int(match.group(4))

            return ''

        while True:
            data = self.jobs_facade.read_log(self.user, idx, offset)
            offset += len(data)
            if len(data) != 0:
                data = data.decode('utf-8')
                data = start_regex.sub(start_fn, data)
                data = end_regex.sub(end_fn, data)

                print(data, file=self.stdout, end='')
            else:
                job = Job.get(Job.id == idx)
                status = job.status
                if status == Status.RUNNING:
                    time.sleep(self.SLEEP_DURATION)
                    continue

                print('Finished with status "%s"' % status.to_str())
                break

    def do_user(self, args):
        """
> user get [user_id]
> user list [email = str]
  [limit = int] [offset = int] [order = (created-desc|created-asc)]
> user count [email = str]
  [limit = int] [offset = int] [order = (created-desc|created-asc)]
> user create [email = str] [role = (master, admin, normal)] [token = str] [public_key = str]
> user update [email = str] [role = (master, admin, normal)] [token = str] [public_key = str]
> user delete [user_id]
        """
        self.route('user', args)

    def user_get(self, args):
        idx, args = self._pop_id(args)
        item = self.users_facade.get(self.user, idx)
        self.pretty_print(item)

    def user_list(self, args):
        result = self.users_facade.list(self.user, **self._parse_list(args))
        self.pretty_print(result)

    def user_count(self, args):
        print(self.users_facade.count(self.user, self._parse_args(args)))

    def user_create(self, args):
        idx = self.users_facade.create(self.user, self._parse_args(args))
        print('Created new user with id = %d' % idx, file=self.stdout)

    def user_update(self, args):
        idx, args = self._pop_id(args)
        args = self._parse_args(args)
        project = self.users_facade.get(self.user, idx)
        del project['id']
        args = {**project, **args}

        self.pretty_print(args)
        if self._confirm_yes():
            self.users_facade.update(self.user, idx, args)
            print('User updated', file=self.stdout)
        else:
            print('Nothing happened', file=self.stdout)

    def user_delete(self, args):
        idx, args = self._pop_id(args)
        self.users_facade.delete(self.user, idx)
        print('Deleted user with id = %d' % idx, file=self.stdout)

    def do_runner(self, args):
        """
> runner get [runner_id]
> runner list [group = str]
  [limit = int] [offset = int]
> runner count [group = str]
> runner create [group = str] [token = str]
> runner update [group = str] [token = str]
> runner delete [runner_id]
        """
        self.route('runner', args)

    def runner_get(self, args):
        idx, args = self._pop_id(args)
        item = self.runners_facade.get(self.user, idx)
        self.pretty_print(item)

    def runner_list(self, args):
        result = self.runners_facade.list(self.user, **self._parse_list(args))
        self.pretty_print(result)

    def runner_count(self, args):
        print(self.runners_facade.count(self.user, self._parse_args(args)))

    def runner_create(self, args):
        idx = self.runners_facade.create(self.user, self._parse_args(args))
        print('Created new runner with id = %d' % idx, file=self.stdout)

    def runner_update(self, args):
        idx, args = self._pop_id(args)
        args = self._parse_args(args)
        runner = self.runners_facade.get(self.user, idx)
        del runner['id']
        args = {**runner, **args}

        self.pretty_print(args)
        if self._confirm_yes():
            self.runners_facade.update(self.user, idx, args)
            print('User updated', file=self.stdout)
        else:
            print('Nothing happened', file=self.stdout)

    def runner_delete(self, args):
        idx, args = self._pop_id(args)
        self.runners_facade.delete(self.user, idx)
        print('Deleted runner with id = %d' % idx, file=self.stdout)


def main() -> None:
    from piper_core.container import Container
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config',
        help='Configuration file',
        type=Path
    )
    parser.add_argument(
        'user_id',
        help='User id',
        type=int
    )

    parsed = vars(parser.parse_args())
    path = parsed['config'].expanduser()
    config = yaml.load(path.open())

    container = Container(config)
    connection = container.get_db()
    database_proxy.initialize(connection)

    user_id = parsed['user_id']
    logged_user = User.get(User.id == user_id)

    shell = container.get_shell(logged_user)
    shell.cmdloop()


if __name__ == '__main__':
    main()
