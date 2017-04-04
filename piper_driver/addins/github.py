import re
from typing import List

import requests

from piper_driver.addins.git import Repository, Branch, Commit


def parse_webhook(hook) -> List[Commit]:
    # https://developer.github.com/v3/activity/events/types/#pushevent
    # tl;dr; If there is no `action` in payload => Push Event
    if 'action' in hook:
        raise Exception
    if 'repository' not in hook:
        raise Exception
    if type(hook['repository']) is not dict:
        raise Exception
    if 'clone_url' not in hook['repository']:
        raise Exception
    if type(hook['repository']['clone_url']) is not str:
        raise Exception
    if 'ref' not in hook:
        raise Exception
    if type(hook['ref']) is not str:
        raise Exception
    if 'commits' not in hook:
        raise Exception
    if type(hook['commits']) is not list:
        raise Exception

    for row in hook['commits']:
        if 'id' not in row:
            raise Exception
        if 'message' not in row:
            raise Exception
        if type(row['id']) is not str:
            raise Exception
        if type(row['message']) is not str:
            raise Exception

    repository = Repository(origin=hook['repository']['clone_url'])
    branch = Branch(ref=hook['ref'], repository=repository)
    commits = []
    for row in hook['commits']:
        commit = Commit(sha=row['id'], message=row['message'], branch=branch)
        commits.append(commit)

    return commits


def fetch_piper_yml(commit: Commit) -> str:
    origin = commit.branch.repository.origin
    # https://raw.githubusercontent.com/<user>/<repo>/<hash>/<path>
    # origin: https://github.com/<user>/<repo>.git
    # origin: git@github.com:francma/piper-ci-test-repo.git
    m = re.match(r'(?:https:\/\/|git@)github\.com(?::|\/)(.*)\/(.*)\.git$', origin)
    if not m:
        raise Exception

    user, repo = m.groups()
    path = 'piper.yml'
    url = 'https://raw.githubusercontent.com/{}/{}/{}/{}'.format(user, repo, commit.sha, path)
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        # TODO use git pull
        raise Exception

    return response.content.decode()

    raise NotImplementedError

