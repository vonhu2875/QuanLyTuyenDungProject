import hashlib

from rapp.dao import add_user
from rapp.test.test_base import test_session, test_app
from rapp.models import User

def test_success(test_session):
    add_user(name='Võ Thị Bích Như', username='a'*5, password='4aA' * 4, avatar=None, email='abc@gmail.com', phone='0123456789', user_role='ADMIN')
    u = User.query.filter(User.username.__eq__('a'*5)).first()
    assert u is not None
    assert u.name == 'Võ Thị Bích Như'
    assert u.password == str(hashlib.md5(('4aA' * 4).encode('utf-8')).hexdigest())