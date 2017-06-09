import tempfile
import os

from piper_driver.models import *
from piper_driver.addins import authorized_keys


def test_1(connection):
    user1 = User.create(role=UserRole.NORMAL, email='1@a.cz', public_key='ssh-rsa AAA')
    user2 = User.create(role=UserRole.NORMAL, email='2@a.cz', public_key='ssh-rsa AAA')
    user3 = User.create(role=UserRole.NORMAL, email='3@a.cz', public_key='ssh-rsa AAA')
    users = [user1, user2, user3]
    user4 = User.create(role=UserRole.NORMAL, email='4@a.cz', public_key='ssh-rsa AAA')

    with tempfile.TemporaryDirectory() as d:
        key_file = os.path.join(d, 'keys')
        with open(key_file, 'a'):
            pass

        authorized_keys.write(key_file, [user4])
        with open(key_file, 'r') as fp:
            line = '{} {} {}|{}'.format(authorized_keys.COMMAND.format(user4.id), user4.public_key, user4.email, authorized_keys.KEY_COMMENT)
            assert line == fp.readline().strip()
            assert '' == fp.readline()

        with open(key_file, 'w') as fp:
            print('ssh-rsa ...', file=fp)

        authorized_keys.write(key_file, users)

        with open(key_file, 'r') as fp:
            assert 'ssh-rsa ...' == fp.readline().strip()
            for user in users:
                line = '{} {} {}|{}'.format(authorized_keys.COMMAND.format(user.id), user.public_key, user.email, authorized_keys.KEY_COMMENT)
                assert line == fp.readline().strip()
            assert '' == fp.readline()

