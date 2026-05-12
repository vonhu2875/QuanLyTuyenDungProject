from rapp.exceptions import DuplicateError
from rapp.test.test_base import test_client, test_app
from rapp.dao import ValidationError
from rapp.dao import UserRole

def test_register_view(test_client, mocker):
    mock_render = mocker.patch("rapp.index.render_template", return_value="Trang")
    res = test_client.get('/register')

    assert res.status_code == 200
    args, kwargs = mock_render.call_args
    assert UserRole.EMPLOYER in kwargs['UserRole']

def test_register_success(test_client, mocker):
    mock_add = mocker.patch("rapp.dao.add_user", return_value=True)
    mocker.patch("rapp.index.render_template", return_value="Trang Register")
    res = test_client.post('/register', data={
        'name': 'Nguyen Van A',
        'username': 'nguyenvana',
        'password': 'Password123',
        'confirm': 'Password123',
        'email': 'a@gmail.com',
        'phone': '0123456789',
        'user_role': 'CANDIDATE'
    })
    assert res.status_code == 302
    assert res.location.endswith('/login')
    mock_add.assert_called_once()

def test_register_password_invalid(test_client, mocker):
    mock_add = mocker.patch("rapp.dao.add_user")
    mock_render = mocker.patch("rapp.index.render_template", return_value="Trang Register")

    res = test_client.post('/register', data={
        'password': 'Password123',
        'confirm': 'KhacNhau123',
        'user_role': 'CANDIDATE'
    })

    assert res.status_code == 200
    mock_add.assert_not_called()

    args, kwargs = mock_render.call_args
    assert kwargs['err_msg'] == "Mật khẩu không khớp!"
    mock_render.assert_called_once()


#ValidationError
def test_register_username_invalid(test_client, mocker):
    mock_add = mocker.patch("rapp.dao.add_user",
                 side_effect=ValidationError("Loi du lieu"))
    mock_render = mocker.patch("rapp.index.render_template", return_value="Trang Register")

    res = test_client.post('/register', data={
        'username': 'abc',
        'password': 'Password123',
        'confirm': 'Password123',
        'user_role': 'CANDIDATE'
    })

    assert res.status_code == 200
    args, kwargs = mock_render.call_args
    assert "Loi du lieu" in kwargs['err_msg']
    assert "Trang Register" in res.get_data(as_text=True)
    mock_render.assert_called_once()
    mock_add.assert_called_once()

#DuplicationError
def test_register_duplicated(test_client, mocker):
    mock_add = mocker.patch("rapp.dao.add_user",
                 side_effect=DuplicateError("Du lieu bi trung"))
    mock_render = mocker.patch("rapp.index.render_template", return_value="Trang Register")

    res = test_client.post('/register', data={
        'username': 'abc',
        'password': 'Password123',
        'confirm': 'Password123',
        'user_role': 'CANDIDATE'
    })

    assert res.status_code == 200
    assert "Trang Register" in res.get_data(as_text=True)
    mock_render.assert_called_once()
    args, kwargs = mock_render.call_args
    assert "Du lieu bi trung" in kwargs['err_msg']
    mock_add.assert_called_once()