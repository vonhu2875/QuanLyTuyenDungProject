import pytest
from datetime import datetime, timedelta
from rapp.dao import add_job
from rapp.exceptions import ValidationError, DuplicateError
from rapp.models import UserRole
from rapp.test.test_base import test_session, test_app

def test_success(test_session):
    j = add_job(title = 'a'*10, description='abc', salary=10000000, deadline= datetime.now() + timedelta(days=50),
                category_id=1, employer_id=1, user_role=UserRole.ADMIN)
    assert j is not None
    assert j.title == 'a'*10
    assert j.description == 'abc'
    assert j.salary == 10000000

@pytest.mark.parametrize('role', [' ', None, UserRole.CANDIDATE, 'EMPLOYER'])
def test_invalid_role(role):
    with pytest.raises(ValidationError, match='Bạn không có quyền đăng tin!'):
        add_job(title='a' * 10, description='abc', salary=10000000, deadline=datetime.now() + timedelta(days=50),
                    category_id=1, employer_id=1, user_role=role)

@pytest.mark.parametrize('title', ['',None])
def test_invalid_empty_title(title):
    with pytest.raises(ValidationError, match="Phải có tiêu đề!"):
        add_job(title=title, description='abc', salary=10000000, deadline=datetime.now() + timedelta(days=50),
                category_id=1, employer_id=1, user_role=UserRole.ADMIN)

@pytest.mark.parametrize('title', ['a'*9,' '*10])
def test_invalid_min_title(title):
    with pytest.raises(ValidationError, match="Tiêu đề phải tối thiểu 10 ký tự!"):
        add_job(title=title, description='abc', salary=10000000, deadline=datetime.now() + timedelta(days=50),
                category_id=1, employer_id=1, user_role=UserRole.ADMIN)


def test_invalid_max_title(test_session):
    with pytest.raises(ValidationError, match="Tiêu đề chỉ tối đa 255 ký tự!"):
        add_job(title='a' * 256, description='abc', salary=10000000, deadline=datetime.now() + timedelta(days=50),
                category_id=1, employer_id=1, user_role=UserRole.ADMIN)

@pytest.mark.parametrize('salary', ['a', ' ', '!', '2a', None])
def test_invalid_type_salary(salary):
    with pytest.raises(ValidationError, match="Lương phải là số"):
        add_job(title='a' * 10, description='abc', salary=salary, deadline=datetime.now() + timedelta(days=50),
                category_id=1, employer_id=1, user_role=UserRole.ADMIN)

@pytest.mark.parametrize('salary', [-1, -999, 0])
def test_invalid_salary(salary):
    with pytest.raises(ValidationError, match="Lương phải > 0!"):
        add_job(title='a' * 10, description='abc', salary=salary, deadline=datetime.now() + timedelta(days=50),
                category_id=1, employer_id=1, user_role=UserRole.ADMIN)

def test_invalid_deadline(test_session):
    with pytest.raises(ValidationError, match="Deadline phải lớn hơn ngày tháng năm hiện tại!"):
        add_job(title='a' * 10, description='abc', salary=200000, deadline=datetime.now() - timedelta(minutes=1),
                category_id=1, employer_id=1, user_role=UserRole.ADMIN)
# Có phát hiện ra lỗi, khi set trễ hơn 1 phút -> Đã chỉnh lại code thành deadline < now thay vì deadline.date()

def test_invalid_max_deadline(test_session):
    with pytest.raises(ValidationError, match="Hạn deadline chỉ tối đa 1 năm kể từ ngày tạo tin!"):
        add_job(title='a' * 10, description='abc', salary=200000, deadline=datetime.now() + timedelta(days=365) + timedelta(minutes=1),
                category_id=1, employer_id=1, user_role=UserRole.ADMIN)

def test_existing_job(test_session):
    add_job(title='Tuyển dụng lập trình viên Java', description='abc', salary=200000,
            deadline=datetime.now() + timedelta(days=1),
            category_id=1, employer_id=1, user_role=UserRole.ADMIN)
    with pytest.raises(DuplicateError, match="Tin tuyển dụng đã tồn tại!"):
        add_job(title='tuyển dụng Lập trình viên Java', description='dfx', salary=708000,
                deadline=datetime.now() + timedelta(days=365),
                category_id=2, employer_id=1, user_role=UserRole.ADMIN)



