from typing import Iterable
from pathlib import Path

from piper_core.model import User

KEY_COMMENT = 'PIPER_GENERATED'
# command="piper-shell [config_path] [user_id]",...
COMMAND = 'command="piper-shell {} {}",no-port-forwarding,no-X11-forwarding'


def write(path: Path, config: Path, users: Iterable[User]) -> None:
    config = config.absolute()
    with path.open('r') as fp:
        preserve = [line for line in fp if not line.strip().endswith(KEY_COMMENT)]
    with path.open('w') as fp:
        for line in preserve:
            fp.write(line)
        for user in users:
            line = '{} {} {}|{}'.format(COMMAND.format(config, user.id), user.public_key, user.email, KEY_COMMENT)
            fp.write(line + '\n')
