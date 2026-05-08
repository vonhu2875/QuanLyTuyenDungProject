from rapp.test.test_base import test_client, test_app
from rapp.models import UserRole
from rapp.exceptions import ValidationError


# 1. TEST API PROFILE
def test_api_view_profile(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 10
        name = "Nguyễn Văn Hà"
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('flask_login.current_user', FakeUser())

    # Giả lập render_template trả về một chuỗi có chứa tên user
    mock_render = mocker.patch("rapp.index.render_template", return_value="Profile của Nguyễn Văn Hà")

    res = test_client.get('/profile')

    assert res.status_code == 200
    mock_render.assert_called_once()
    assert "Nguyễn Văn Hà" in res.get_data(as_text=True)


# TEST XEM CHI TIẾT VIỆC LÀM
def test_api_get_job_detail_success(test_client, mocker):
    class FakeUser():
        is_authenticated = True
        id = 1
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())

    # Giả lập 1 đối tượng Job trả về từ DAO
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