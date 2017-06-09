import json

from piper_driver.addins.git import *
from piper_driver.addins.github import parse_webhook, fetch_piper_yml


def test_push_hook():
    with open('tests/webhooks/github_push.json') as fd:
        contents = json.load(fd)

    commit = parse_webhook(contents)

    assert commit.branch.name == 'master'
    assert commit.branch.repository.origin == 'https://github.com/olipo186/Git-Auto-Deploy.git'
    assert commit.sha == 'b60ff44438d884b200d70de9c45fec5a15f2c0fa'


def test_pull_request_closed_positive_hook():
    pass


def test_pull_request_closed_negative_hook():
    pass


def test_not_push_hook():
    pass


def test_fetch_piper_yml():
    repo = Repository(origin='git@github.com:francma/piper-ci-test-repo.git')
    branch = Branch(name='master', repository=repo)
    commit = Commit(sha='d9346cf45f551bce7f02c810e44fbc9776734baf', branch=branch, message='EMPTY')

    fetch_piper_yml(commit)



