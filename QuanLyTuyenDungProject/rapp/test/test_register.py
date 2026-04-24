import hashlib
import pytest
from rapp.dao import add_user
from rapp.exceptions import ValidationError, DuplicateError
from rapp.test.test_base import test_session, test_app, mock_cloudinary
from rapp.models import User, UserRole

def test_success_role_candidate(test_session):
    add_user(name='Võ Thị Bích Như', username='a'*5, password='4aA' * 3, avatar=None, email='abc@gmail.com', phone='0123456789', user_role=UserRole.CANDIDATE)
    u = User.query.filter(User.username.__eq__('a'*5)).first()
    assert u is not None
    assert u.name == 'Võ Thị Bích Như'
    assert u.user_role == UserRole.CANDIDATE
    assert u.password == str(hashlib.md5(('4aA' * 3).encode('utf-8')).hexdigest())

def test_success_role_employer(test_session):
    add_user(name='Võ Thị Bích Như', username='a'*5, password='4aA' * 3, avatar=None, email='abc@gmail.com', phone='0123456789', user_role=UserRole.EMPLOYER)
    u = User.query.filter(User.username.__eq__('a'*5)).first()
    assert u is not None
    assert u.name == 'Võ Thị Bích Như'
    assert u.user_role == UserRole.EMPLOYER
    assert u.password == str(hashlib.md5(('4aA' * 3).encode('utf-8')).hexdigest())

@pytest.mark.parametrize('password', ['2aA'* 2, 'aA' * 4,  '2a' * 4, '2' * 8])
def test_invalid_password(password):
    with pytest.raises(ValidationError):
        add_user(name='Võ Thị Bích Như', username='a'*5, password=password, avatar=None, email='abc@gmail.com', phone='0123456789', user_role=UserRole.EMPLOYER)

@pytest.mark.parametrize('username', ['a' * 4, 'a' * 21, 'a '* 3, 'a!' * 3])
def test_invalid_username(username):
    with pytest.raises(ValidationError):
        add_user(name='Võ Thị Bích Như', username=username, password='4aA' * 3, avatar=None, email='abc@gmail.com',
                 phone='0123456789', user_role=UserRole.EMPLOYER)

@pytest.mark.parametrize('email', ['123', ' ', 'abc', 'abc@', '@gmail.com'])
def test_invalid_email(email):
    with pytest.raises(ValidationError):
        add_user(name='Võ Thị Bích Như', username='a' * 5, password='4aA' * 3, avatar=None, email=email,
                 phone='0123456789', user_role=UserRole.EMPLOYER)

@pytest.mark.parametrize('name', [' ', 'a' * 256])
def test_invalid_name(name):
    with pytest.raises(ValidationError):
        add_user(name=name, username='a'*5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
                 phone='0123456789', user_role=UserRole.CANDIDATE)

@pytest.mark.parametrize('user_role', [None, ' ', 'CANDIDATE', UserRole.ADMIN])
def test_invalid_user_role(user_role):
    with pytest.raises(ValidationError):
        add_user(name='Võ Thị Bích Như', username='a'*5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
                 phone='0123456789', user_role=user_role)


@pytest.mark.parametrize('phone', [None, ' ', '01'*8, '0a' * 7])
def test_invalid_phone(phone):
    with pytest.raises(ValidationError):
        add_user(name='Võ Thị Bích Như', username='a' * 5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
                 phone=phone, user_role=UserRole.CANDIDATE)

def test_existing_username(test_session):
    add_user(name='Võ Thị Bích Như', username='a' * 5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
             phone='0123456789', user_role=UserRole.CANDIDATE)
    with pytest.raises(DuplicateError):
        add_user(name='Nguyễn Văn A', username='a' * 5, password='4aA' * 3, avatar=None, email='def@gmail.com',
                 phone='0123456789', user_role=UserRole.CANDIDATE)

def test_existing_email(test_session):
    add_user(name='Võ Thị Bích Như', username='a' * 5, password='4aA' * 3, avatar=None, email='abc@gmail.com',
             phone='0123456789', user_role=UserRole.CANDIDATE)
    with pytest.raises(DuplicateError):
        add_user(name='Nguyễn Văn B', username='ab' * 3, password='4aA' * 3, avatar=None, email='abc@gmail.com',
                 phone='0123456789', user_role=UserRole.CANDIDATE)

def test_avatar(test_session, mock_cloudinary):
    add_user(name='Võ Thị Bích Như', username='a'*5, password='4aA' * 3, avatar='abc', email='abc@gmail.com', phone='0123456789', user_role=UserRole.CANDIDATE)
    u = User.query.filter(User.username.__eq__('a' * 5)).first()
    assert u.avatar == 'https://fake-avatar.png'