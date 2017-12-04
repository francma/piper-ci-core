import tempfile
import os
from pathlib import Path

from piper_core.container import Container
from piper_core.model import *
from piper_core.utils import authorized_keys


def test_1(container: Container):
    assert container
    user1 = User.create(role=UserRole.NORMAL, email='1@a.cz', public_key='ssh-rsa AAA')
    user2 = User.create(role=UserRole.NORMAL, email='2@a.cz', public_key='ssh-rsa AAB')
    user3 = User.create(role=UserRole.NORMAL, email='3@a.cz', public_key='ssh-rsa AAC')
    users = [user1, user2, user3]
    user4 = User.create(role=UserRole.NORMAL, email='4@a.cz', public_key='ssh-rsa AAD')

    config_path = Path('/home/config.yml')

    with tempfile.TemporaryDirectory() as d:
        key_file = Path(os.path.join(d, 'keys'))
        with open(key_file, 'a'):
            pass

        authorized_keys.write(key_file, config_path, [user4])
        with open(key_file, 'r') as fp:
            line = '{} {} {}|{}'.format(authorized_keys.COMMAND.format(config_path, user4.id), user4.public_key,
                                        user4.email, authorized_keys.KEY_COMMENT)
            assert line == fp.readline().strip()
            assert '' == fp.readline()

        with open(key_file, 'w') as fp:
            fp.write('ssh-rsa ...\n')

        authorized_keys.write(key_file, config_path, users)

        with open(key_file, 'r') as fp:
            assert 'ssh-rsa ...' == fp.readline().strip()
            for user in users:
                line = '{} {} {}|{}'.format(authorized_keys.COMMAND.format(config_path, user.id),
                                            user.public_key, user.email, authorized_keys.KEY_COMMENT)
                assert line == fp.readline().strip()
            assert '' == fp.readline()
