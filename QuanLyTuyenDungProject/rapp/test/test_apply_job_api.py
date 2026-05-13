import io

from rapp.test.test_base import test_client, test_app
from rapp.models import UserRole
from rapp.exceptions import ValidationError


# 1. TEST NỘP HỒ SƠ THÀNH CÔNG (POST)
def test_api_apply_job_success(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 10
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('flask_login.current_user', return_value=FakeUser())

    mock_job = mocker.Mock()
    mock_job.id = 1
    mock_job.title = "Python Developer"
    mocker.patch("rapp.dao.get_job_by_id", return_value=mock_job)

    mock_apply = mocker.patch("rapp.dao.apply_for_job")
    mock_render = mocker.patch("rapp.index.render_template", return_value="Thanh Cong")

    data = {
        'cv_file': (io.BytesIO(b"%PDF-1.5 test"), 'my_cv.pdf')
    }

    res = test_client.post('/jobs/1/applications', data=data, content_type='multipart/form-data')

    assert res.status_code == 200
    assert "Thanh Cong" in res.get_data(as_text=True)

    mock_apply.assert_called_once()
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert "Nộp hồ sơ thành công" in kwargs['succ_msg']


# 2. TEST NỘP HỒ SƠ THẤT BẠI (Do DAO ném lỗi - ví dụ nộp trùng hoặc sai định dạng)
def test_api_apply_job_validation_error(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 10
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('flask_login.current_user', return_value=FakeUser())

    mock_job = mocker.Mock()
    mock_job.id = 1
    mocker.patch("rapp.dao.get_job_by_id", return_value=mock_job)

    # Giả lập hàm DAO ném lỗi ValidationError
    msg_error = "Bạn đã nộp hồ sơ cho công việc này rồi!"
    mocker.patch("rapp.dao.apply_for_job", side_effect=ValidationError(msg_error))
    mock_render = mocker.patch("rapp.index.render_template", return_value="Trang Loi")

    data = {
        'cv_file': (io.BytesIO(b"%PDF-1.5"), 'cv.pdf')
    }

    res = test_client.post('/jobs/1/applications', data=data, content_type='multipart/form-data')

    assert res.status_code == 200
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert kwargs['err_msg'] == msg_error


# 3. TEST XEM DANH SÁCH ĐÃ NỘP
def test_api_get_my_applications(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 10
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('flask_login.current_user', return_value=FakeUser())

    fake_list = [{"job_title": "Python Dev", "status": "PENDING"}]
    mock_get_apps = mocker.patch("rapp.dao.get_my_applications", return_value=fake_list)
    mock_render = mocker.patch("rapp.index.render_template", return_value="My Apps Page")

    res = test_client.get('/profile/applications')

    assert res.status_code == 200
    mock_get_apps.assert_called_once_with(10)
    assert "My Apps Page" in res.get_data(as_text=True)


# 4. TEST EMPLOYER KHÔNG ĐƯỢC NỘP ĐƠN
def test_api_apply_job_unauthorized(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 5
        user_role = UserRole.EMPLOYER

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('flask_login.current_user', return_value=FakeUser())

    mock_job = mocker.Mock()
    mock_job.id = 1
    mocker.patch("rapp.dao.get_job_by_id", return_value=mock_job)

    res = test_client.post('/jobs/1/applications', data={'cv_file': (io.BytesIO(b""), "a.pdf")})

    assert res.status_code == 200
    assert "403 - Lỗi quyền truy cập" in res.get_data(as_text=True)

# 5. TEST XEM CHI TIẾT VIỆC LÀM
def test_api_get_job_detail_success(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 1
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())

    mock_job = mocker.Mock()
    mock_job.id = 1
    mock_job.title = "Lập trình viên React"

    mocker.patch("rapp.dao.get_job_by_id", return_value=mock_job)
    mock_render = mocker.patch("rapp.index.render_template", return_value="Job Detail HTML")

    res = test_client.get('/jobs/1')

    assert res.status_code == 200
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert kwargs['job'].title == "Lập trình viên React"