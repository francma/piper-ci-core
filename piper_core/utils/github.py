import re
from typing import Dict, Any

import requests
import yaml
from jsonschema import Draft4Validator, ValidationError

from piper_core.utils.git import *
from piper_core.utils.exceptions import *


class Github:

    def __init__(self, schema):
        self._schema = schema

    def parse_webhook(self, hook: Dict[Any, Any]) -> Commit:
        # https://developer.github.com/v3/activity/events/types/#pushevent
        # tl;dr; If there is no `action` in payload -> Push Event
        hook_schema = self._schema['components']['schemas']['github-hook']
        try:
            Draft4Validator(schema=hook_schema).validate(hook)
        except ValidationError as e:
            raise WebhookParseException(e.message)

        if 'action' in hook:
            raise WebhookParseException

        repository = Repository(origin=hook['repository']['clone_url'])
        branch = Branch(repository=repository, name=hook['ref'].split('/')[-1])
        commit = Commit(branch=branch, sha=hook['after'], message='')

        return commit

    def fetch_piper_yml(self, commit: Commit) -> Dict[Any, Any]:
        # https://raw.githubusercontent.com/<user>/<repo>/<hash>/<path>
        # origin: https://github.com/<user>/<repo>.git
        # origin: git@github.com:francma/piper-ci-test-repo.git
        m = re.match(r'^(?:https://|git@)github\.com[:/](.*)/(.*)\.git$', commit.branch.repository.origin)
        if not m:
            raise WebhookParseException

        user, repo = m.group(1), m.group(2)
        url = 'https://raw.githubusercontent.com/{}/{}/{}/{}'.format(user, repo, commit.sha, 'piper.yml')
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            contents = response.content.decode()
        else:
            raise WebhookParseException(url)

        return yaml.load(contents)
