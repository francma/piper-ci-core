from typing import Iterable

from piper_driver.models import User

KEY_COMMENT = 'piper_generated'
COMMAND = 'command="piper-shell {}",no-port-forwarding,no-X11-forwarding'


def write(path, users: Iterable[User]) -> None:
    with open(path, 'r') as fp:
        preserve = [line for line in fp if not line.endswith(KEY_COMMENT)]
    with open(path, 'w') as fp:
        for line in preserve:
            print(line, file=fp, end='')
        for user in users:
            line = '{} {} {}|{}'.format(COMMAND.format(user.id), user.public_key, user.email, KEY_COMMENT)
            print(line, file=fp)



