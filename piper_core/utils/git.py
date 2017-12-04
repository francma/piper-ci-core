import subprocess


class GitCloneException(Exception):
    pass


def validate_origin(origin: str) -> bool:
    command = ['git', 'ls-remote', origin]
    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    process.communicate()

    return process.returncode == 0


class Repository:

    def __init__(self, origin: str) -> None:
        self._origin = origin

    @property
    def origin(self):
        return self._origin


class Branch:

    def __init__(self, name: str, repository: Repository) -> None:
        self._name = name
        self._repository = repository

    @property
    def name(self):
        return self._name

    @property
    def repository(self):
        return self._repository


class Commit:

    def __init__(self, sha: str, branch: Branch, message: str=None) -> None:
        self._sha = sha
        self._branch = branch
        self._message = message

    @property
    def sha(self):
        return self._sha

    @property
    def branch(self):
        return self._branch

    @property
    def message(self):
        return self._message

    def clone(self, destination: str):
        command = ['git', 'clone', '--recursive', '--branch', self.branch, self.branch.repository.origin, '.']
        process = subprocess.Popen(
            command,
            cwd=str(destination),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        out, err = process.communicate()
        if process.returncode != 0:
            raise GitCloneException(err)

        command = ['git', 'checkout', '-f', self.sha]
        process = subprocess.Popen(
            command,
            cwd=str(destination),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        out, err = process.communicate()
        if process.returncode != 0:
            raise GitCloneException(err)
