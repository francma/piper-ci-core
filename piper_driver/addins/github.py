import re
from typing import List, Dict, Any

import requests
import yaml

from piper_driver.addins.git import *


def parse_webhook(hook: Dict[Any, Any]) -> Commit:
    # https://developer.github.com/v3/activity/events/types/#pushevent
    # tl;dr; If there is no `action` in payload => Push Event
    if 'action' in hook:
        raise Exception

    if 'repository' not in hook or type(hook['repository']) is not dict:
        raise Exception
    if 'clone_url' not in hook['repository'] or type(hook['repository']['clone_url']) is not str:
        raise Exception
    if 'ref' not in hook or type(hook['ref']) is not str:
        raise Exception
    if 'after' not in hook or type(hook['after']) is not str:
        raise Exception

    repository = Repository(origin=hook['repository']['clone_url'])
    branch = Branch(repository=repository, name=hook['ref'].split('/')[-1])
    commit = Commit(branch=branch, sha=hook['after'], message='')

    return commit


def fetch_piper_yml(commit: Commit) -> Dict[Any, Any]:
    # https://raw.githubusercontent.com/<user>/<repo>/<hash>/<path>
    # origin: https://github.com/<user>/<repo>.git
    # origin: git@github.com:francma/piper-ci-test-repo.git
    m = re.match(r'(?:https:\/\/|git@)github\.com(?::|\/)(.*)\/(.*)\.git$', commit.branch.repository.origin)
    if not m:
        raise Exception

    user, repo = m.groups()
    path = 'piper.yml'
    url = 'https://raw.githubusercontent.com/{}/{}/{}/{}'.format(user, repo, commit.sha, path)
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        contents = response.content.decode()

    return yaml.load(contents)

