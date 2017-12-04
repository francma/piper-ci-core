from piper_core.container import Container
from piper_core.model import *


def test_facade_get(container: Container):
    users_facade = container.get_users_facade()
    user = User.create(role=UserRole.MASTER, email='email@email.cz', public_key='ssh-rsa AAA')

    assert users_facade.get(user, user.id)


def test_facade_list_count(container: Container):
    users_facade = container.get_users_facade()

    user = User.create(role=UserRole.MASTER, email='email1@email.cz', public_key='ssh-rsa AAAA')
    User.create(role=UserRole.MASTER, email='email2@email.cz', public_key='ssh-rsa AAAB')
    User.create(role=UserRole.MASTER, email='email3@email.cz', public_key='ssh-rsa AAAC')

    assert users_facade.list(user)
    assert users_facade.count(user)


def test_facade_create(container: Container):
    users_facade = container.get_users_facade()
    user = User.create(role=UserRole.MASTER, email='email1@email.cz', public_key='ssh-rsa AAAA')

    users_facade.create(user, {
        'email': 'email2@email.com',
        'role': str(UserRole.ADMIN).lower(),
        'public_key': 'ssh-rsa AAAAb===',
    })
    assert users_facade.count(user) == 2


def test_facade_update(container: Container):
    users_facade = container.get_users_facade()
    user = User.create(role=UserRole.MASTER, email='email1@email.cz', public_key='ssh-rsa AAA')
    user2 = User.create(role=UserRole.NORMAL, email='email2@email.cz', public_key='ssh-rsa AAB')

    users_facade.update(user, user2.id, {
        'email': 'test@test.cz',
        'role': str(UserRole.ADMIN).lower(),
        'public_key': 'ssh-rsa AAAAb===',
    })
    user2 = User.get(User.id == user2.id)
    assert user2.email == 'test@test.cz'
    assert user2.role == UserRole.ADMIN
