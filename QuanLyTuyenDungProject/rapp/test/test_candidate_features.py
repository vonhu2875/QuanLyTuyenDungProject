import pytest
from rapp import dao
from rapp.models import User, Application, Job
from rapp.test.test_base import test_session, job_to_apply, sample_candidate, test_app, sample_category, sample_employer




# 1. Kiểm tra lấy job thành công
def test_get_job_by_id_success(test_session, job_to_apply):
    job = dao.get_job_by_id(job_to_apply.id)
    assert job is not None
    assert job.title == job_to_apply.title

# 2. Kiểm tra với ID không tồn tại
def test_get_job_by_id_not_found(test_session):
    job = dao.get_job_by_id(9999)
    assert job is None

# 3. Ứng viên đã nộp hồ sơ cho một công việc cụ thể chưa
def test_check_applied(test_session, job_to_apply, sample_candidate):
    # Ban đầu chưa nộp
    assert dao.check_applied(sample_candidate.id, job_to_apply.id) is False

    # Giả lập nộp hồ sơ bằng cách thêm trực tiếp vào DB
    new_app = Application(job_id=job_to_apply.id, candidate_id=sample_candidate.id, cv_path="test.pdf")
    test_session.add(new_app)
    test_session.commit()

    assert dao.check_applied(sample_candidate.id, job_to_apply.id) is True

# 4. Kiểm tra xem dữ liệu trong Database có thực sự thay đổi sau khi gọi hàm
def test_update_user_profile_success(test_session, sample_candidate):
    data = {
        'name': 'Nguyễn Văn A',
        'email': 'vana@gmail.com',
        'phone': '0987654321'
    }

    result = dao.update_user_profile(sample_candidate.id, data)

    assert result is True
    # Truy vấn lại từ DB để kiểm tra tính chính xác
    user = User.query.get(sample_candidate.id)
    assert user.name == 'Nguyễn Văn A'
    assert user.email == 'vana@gmail.com'
    assert user.phone == '0987654321'

# 5. Test cập nhật cho user không tồn tại
def test_update_user_profile_fail(test_session):

    result = dao.update_user_profile(9999, {})
    assert result is False

# 6. Test hàm lấy hồ sơ
def test_get_my_applications_list(test_session, sample_candidate, job_to_apply):

    # Tạo 1 hồ sơ mẫu
    app = Application(job_id=job_to_apply.id, candidate_id=sample_candidate.id, cv_path="link.pdf")
    test_session.add(app)
    test_session.commit()

    apps = dao.get_my_applications(sample_candidate.id)
    assert len(apps) >= 1
    assert apps[0].job_id == job_to_apply.id
    assert apps[0].candidate_id == sample_candidate.id