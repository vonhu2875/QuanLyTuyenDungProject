from rapp.test.test_base import test_client, test_app
from rapp.exceptions import ValidationError
from rapp.models import UserRole



# ==================== update_status ====================

def test_update_status_success(test_client, mocker):
    """EMPLOYER cập nhật trạng thái thành công → redirect về manage_applications"""
    class FakeUser:
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    class FakeApplication:
        id = 1
        job_id = 1

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_application_by_id', return_value=FakeApplication())
    mock_update = mocker.patch('rapp.index.dao.update_application_status', return_value=FakeApplication())

    res = test_client.patch('/applications/1/status', data={'status': 'INTERVIEW'})

    assert res.status_code == 302
    assert 'applications' in res.location
    mock_update.assert_called_once()


def test_update_status_validation_error(test_client, mocker):
    """ValidationError → redirect về manage_applications kèm flash message"""
    class FakeUser:
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    class FakeApplication:
        id = 1
        job_id = 1

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_application_by_id', return_value=FakeApplication())
    mocker.patch('rapp.index.dao.update_application_status',
                 side_effect=ValidationError("Hồ sơ đã ở trạng thái cuối, không thể thay đổi!"))

    res = test_client.patch('/applications/1/status', data={'status': 'SUBMITTED'})

    assert res.status_code == 302
    assert 'applications' in res.location


def test_update_status_candidate_forbidden(test_client, mocker):
    """CANDIDATE cố cập nhật → 403"""
    class FakeUser:
        is_authenticated = True
        id = 2
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())

    res = test_client.patch('/applications/1/status', data={'status': 'INTERVIEW'})

    assert res.status_code == 403


def test_update_status_app_not_found(test_client, mocker):
    """Hồ sơ không tồn tại → 404"""
    class FakeUser:
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_application_by_id', return_value=None)

    res = test_client.patch('/applications/999/status', data={'status': 'INTERVIEW'})

    assert res.status_code == 404
