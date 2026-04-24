import hashlib

import pytest

from rapp.dao import auth_user, add_user
from rapp.exceptions import ValidationError
from rapp.models import UserRole
from rapp.test.test_base import test_session, test_app

def test_success(test_session):
    add_user(name='Võ Thị Bích Như', username='a' * 5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
             phone='0123456789', user_role=UserRole.CANDIDATE)
    a = auth_user(username='a' * 5, password="4aA" * 3)
    assert a is not None
    assert a.username == 'a' * 5
    assert a.password == str(hashlib.md5(('4aA' * 3).encode('utf-8')).hexdigest())

def test_empty_username(test_session):
    with pytest.raises(ValidationError, match="Vui lòng nhập username!"):
        a = auth_user(username='', password="4aA" * 3)

def test_empty_password(test_session):
    with pytest.raises(ValidationError, match="Vui lòng nhập mật khẩu!"):
        a = auth_user(username='a' * 5, password='')


def test_invalid_username(test_session):
    add_user(name='Võ Thị Bích Như', username='a' * 5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
             phone='0123456789', user_role=UserRole.CANDIDATE)
    a = auth_user(username='a' * 6, password="4aA" * 3)
    assert a is None

def test_invalid_password(test_session):
    add_user(name='Võ Thị Bích Như', username='a' * 5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
             phone='0123456789', user_role=UserRole.CANDIDATE)
    a = auth_user(username='a' * 5, password="4aA" * 4)
    assert a is None

def test_not_exist_user(test_session):
    a = auth_user(username='a' * 5, password="4aA" * 4)
    assert a is None


def test_inactive_user(test_session):
    u = add_user(name='Võ Thị Bích Như', username='a' * 5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
             phone='0123456789', user_role=UserRole.CANDIDATE)
    u.active = False
    a = auth_user(username='a' * 5, password="4aA" * 3)
    assert a is None

