from rapp.test.test_base import test_client, test_app
import hashlib


def test_login_view(test_client, mocker):
    mocker.patch("rapp.index.render_template", return_value="Trang Login")
    res = test_client.get('/login')
    assert res.status_code == 200
    assert "Trang Login" in res.get_data(as_text=True)

def test_login_success(test_client, mocker):
    class FakeUser():
        id = 1
        username = "admin"
        password = hashlib.md5("Admin@123".encode('utf-8')).hexdigest()

    mock_auth = mocker.patch("rapp.dao.auth_user", return_value=FakeUser())
    mock_login = mocker.patch("rapp.index.login_user", return_value=True)
    res = test_client.post('/login', data={
        'username': 'admin',
        'password': 'Admin@123'
    })
    assert res.status_code == 302
    assert res.location.endswith('/')
    mock_auth.assert_called_once()
    mock_login.assert_called_once()

from rapp.dao import ValidationError  # Nhớ import lỗi này vào bài test


def test_login_exception(test_client, mocker):
    mocker.patch("rapp.dao.auth_user", side_effect=ValidationError("Sai tên đăng nhập hoặc sai mật khẩu!"))

    mock_render = mocker.patch("rapp.index.render_template", return_value="Trang Login")

    res = test_client.post('/login', data={
        'username': 'aaa',
        'password': 'aaa'
    })

    assert res.status_code == 200
    assert "Trang Login" in res.get_data(as_text=True)
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert kwargs['err_msg'] == "Sai tên đăng nhập hoặc sai mật khẩu!"