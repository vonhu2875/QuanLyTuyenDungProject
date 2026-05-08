from rapp.test.test_base import test_client, test_app
from rapp.exceptions import ValidationError
from rapp.models import UserRole


# ==================== manage_applications ====================

def test_manage_applications_employer_own_job(test_client, mocker):
    """EMPLOYER truy cập hồ sơ job của mình → render applications.html"""
    class FakeUser:
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    class FakeJob:
        id = 1
        employer_id = 1
        title = "Lập trình viên Python"

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_job_by_id', return_value=FakeJob())
    mocker.patch('rapp.index.dao.get_applications_by_job', return_value=[])
    mock_render = mocker.patch('rapp.index.render_template', return_value='OK')

    res = test_client.get('/jobs/1/applications')

    assert res.status_code == 200
    args, _ = mock_render.call_args
    assert args[0] == 'applications.html'


def test_manage_applications_employer_other_job(test_client, mocker):
    """EMPLOYER truy cập hồ sơ job của người khác → redirect manage_jobs"""
    class FakeUser:
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    class FakeJob:
        id = 2
        employer_id = 99
        title = "Công việc của người khác"

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_job_by_id', return_value=FakeJob())

    res = test_client.get('/jobs/2/applications')

    assert res.status_code == 302
    assert 'manage_jobs' in res.location


def test_manage_applications_candidate_redirect(test_client, mocker):
    """CANDIDATE truy cập → redirect về trang chủ"""
    class FakeUser:
        is_authenticated = True
        id = 2
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())

    res = test_client.get('/jobs/1/applications')

    assert res.status_code == 302
    assert res.location.endswith('/')


def test_manage_applications_job_not_found(test_client, mocker):
    """Job không tồn tại → redirect manage_jobs"""
    class FakeUser:
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_job_by_id', return_value=None)

    res = test_client.get('/jobs/999/applications')

    assert res.status_code == 302
    assert 'manage_jobs' in res.location


def test_manage_applications_admin_any_job(test_client, mocker):
    """ADMIN truy cập hồ sơ bất kỳ job → render applications.html"""
    class FakeUser:
        is_authenticated = True
        id = 99
        user_role = UserRole.ADMIN

    class FakeJob:
        id = 1
        employer_id = 5
        title = "Công việc bất kỳ"

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_job_by_id', return_value=FakeJob())
    mocker.patch('rapp.index.dao.get_applications_by_job', return_value=[])
    mock_render = mocker.patch('rapp.index.render_template', return_value='OK')

    res = test_client.get('/jobs/1/applications')

    assert res.status_code == 200
    args, _ = mock_render.call_args
    assert args[0] == 'applications.html'


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

    res = test_client.patch('/jobs/1/applications/1/status', data={'status': 'INTERVIEW'})

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

    res = test_client.patch('/jobs/1/applications/1/status', data={'status': 'SUBMITTED'})

    assert res.status_code == 302
    assert 'applications' in res.location


def test_update_status_candidate_forbidden(test_client, mocker):
    """CANDIDATE cố cập nhật → 403"""
    class FakeUser:
        is_authenticated = True
        id = 2
        user_role = UserRole.CANDIDATE

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())

    res = test_client.patch('/jobs/1/applications/1/status', data={'status': 'INTERVIEW'})

    assert res.status_code == 403


def test_update_status_app_not_found(test_client, mocker):
    """Hồ sơ không tồn tại → 404"""
    class FakeUser:
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_application_by_id', return_value=None)

    res = test_client.patch('/jobs/1/applications/999/status', data={'status': 'INTERVIEW'})

    assert res.status_code == 404


def test_update_status_app_wrong_job(test_client, mocker):
    """app_id không thuộc job_id → 404"""
    class FakeUser:
        is_authenticated = True
        id = 1
        user_role = UserRole.EMPLOYER

    class FakeApplication:
        id = 1
        job_id = 99

    mocker.patch('flask_login.utils._get_user', return_value=FakeUser())
    mocker.patch('rapp.index.dao.get_application_by_id', return_value=FakeApplication())

    res = test_client.patch('/jobs/1/applications/1/status', data={'status': 'INTERVIEW'})

    assert res.status_code == 404
