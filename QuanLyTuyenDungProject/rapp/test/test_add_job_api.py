from rapp.test.test_base import test_client, test_app
from rapp.dao import UserRole

def test_create_job_success(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER
    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('flask_login.current_user', return_value=FakeUser())

    mock_add = mocker.patch("rapp.index.add_job")

    res = test_client.post('/jobs', data={
        'title': 'Lập trình viên Python Senior',
        'description': 'Yêu cầu 3 năm kinh nghiệm',
        'salary': '2000',
        'deadline': '2026-12-31',
        'category_id': '1'
    })

    assert res.status_code == 302
    assert res.location.endswith('/')
    mock_add.assert_called_once()


def test_create_job_exception(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('flask_login.current_user', return_value=FakeUser())


    mock_add = mocker.patch("rapp.index.add_job", side_effect=Exception('Tiêu đề phải ít nhất 10 ký tự'))
    mock_render = mocker.patch("rapp.index.render_template", return_value="HTML gia lap")
    res = test_client.post('/jobs', data={
        'title': 'a'*5,
        'description': '...',
        'salary': '1000',
        'deadline': '2026-12-31',
        'category_id': '1'
    })
    assert res.status_code == 200
    assert "HTML gia lap" in res.get_data(as_text=True)
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert kwargs['err_msg'] == 'Tiêu đề phải ít nhất 10 ký tự'
    mock_add.assert_called_once()


def test_create_job_unauthorized(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 2
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('flask_login.current_user', return_value=FakeUser())

    mock_render = mocker.patch("rapp.index.render_template", return_value="Lỗi quyền")

    res = test_client.post('/jobs', data={
        'title': 'a' * 5,
        'description': '...',
        'salary': '1000',
        'deadline': '2026-12-31',
        'category_id': '1'
    })
    assert res.status_code == 200
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert "Bạn không có quyền đăng tin!" in kwargs['err_msg']