import json

from piper_driver.addins.git import *
from piper_driver.addins.github import parse_webhook, fetch_piper_yml


def test_push_hook():
    with open('tests/webhooks/github_push.json') as fd:
        contents = json.load(fd)

    result = parse_webhook(contents)

    expected = set(['b60ff44438d884b200d70de9c45fec5a15f2c0fa', 'b60ff44438d884b200d70de9c45fec5a15f2c0fb'])
    for commit in result:
        assert commit.branch.ref == 'refs/heads/master'
        assert commit.branch.repository.origin == 'https://github.com/olipo186/Git-Auto-Deploy.git'
        assert commit.sha in expected
        expected.remove(commit.sha)
    assert len(expected) == 0


def test_pull_request_closed_positive_hook():
    pass


def test_pull_request_closed_negative_hook():
    pass


def test_not_push_hook():
    pass


def test_fetch_piper_yml():
    repo = Repository(origin='git@github.com:francma/piper-ci-test-repo.git')
    branch = Branch(ref='NOT USED', repository=repo)
    commit = Commit(sha='d9346cf45f551bce7f02c810e44fbc9776734baf', branch=branch, message='EMPTY')

    yml = fetch_piper_yml(commit)
    assert len(yml) != 0



