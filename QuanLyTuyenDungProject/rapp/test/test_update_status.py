import pytest
from datetime import datetime, timedelta
from sqlalchemy import text

from rapp import db
from rapp.dao import update_application_status, get_applications_by_job, get_my_applications
from rapp.exceptions import ValidationError
from rapp.models import User, UserRole, Category, Job, Application, AppStatus
from rapp.test.test_base import test_app, test_session


@pytest.fixture
def setup_nv3(test_session):
    """Tạo dữ liệu mẫu đầy đủ cho NV3:
    - employer_a, employer_b, candidate_a, candidate_b, admin
    - job_a (của employer_a), job_b (của employer_b)
    - app_a (candidate_a nộp vào job_a), app_b (candidate_b nộp vào job_b)
    """
    cat = Category(name="IT")
    test_session.add(cat)
    test_session.flush()

    employer_a = User(name="Employer A", username="employer_a", password="x",
                      user_role=UserRole.EMPLOYER, phone="0901111111", email="emp_a@test.com")
    employer_b = User(name="Employer B", username="employer_b", password="x",
                      user_role=UserRole.EMPLOYER, phone="0902222222", email="emp_b@test.com")
    candidate_a = User(name="Candidate A", username="candidate_a", password="x",
                       user_role=UserRole.CANDIDATE, phone="0903333333", email="cand_a@test.com")
    candidate_b = User(name="Candidate B", username="candidate_b", password="x",
                       user_role=UserRole.CANDIDATE, phone="0904444444", email="cand_b@test.com")
    admin = User(name="Admin", username="admin_user", password="x",
                 user_role=UserRole.ADMIN, phone="0905555555", email="admin@test.com")

    test_session.add_all([employer_a, employer_b, candidate_a, candidate_b, admin])
    test_session.flush()

    job_a = Job(title="Lập trình viên Python Backend",
                description="Yêu cầu 2 năm kinh nghiệm Python",
                salary=20000000,
                deadline=datetime.now() + timedelta(days=30),
                category_id=cat.id,
                employer_id=employer_a.id)
    job_b = Job(title="Thiết kế đồ họa cao cấp",
                description="Yêu cầu kinh nghiệm Photoshop",
                salary=15000000,
                deadline=datetime.now() + timedelta(days=20),
                category_id=cat.id,
                employer_id=employer_b.id)
    test_session.add_all([job_a, job_b])
    test_session.flush()

    app_a = Application(job_id=job_a.id, candidate_id=candidate_a.id, cv_path="https://cv-a.pdf")
    app_b = Application(job_id=job_b.id, candidate_id=candidate_b.id, cv_path="https://cv-b.pdf")
    test_session.add_all([app_a, app_b])
    test_session.commit()

    return {
        "employer_a": employer_a,
        "employer_b": employer_b,
        "candidate_a": candidate_a,
        "candidate_b": candidate_b,
        "admin": admin,
        "job_a": job_a,
        "job_b": job_b,
        "app_a": app_a,
        "app_b": app_b,
        "cat": cat,
    }


# ===== Nhóm 1: Kiểm tra phân quyền cập nhật (ràng buộc a) =====

def test_tc1_1_employer_updates_own_job(setup_nv3):
    """TC1.1: EMPLOYER A cập nhật hồ sơ thuộc job của EMPLOYER A → Thành công"""
    d = setup_nv3
    result = update_application_status(
        app_id=d["app_a"].id,
        new_status="INTERVIEW",
        updater_id=d["employer_a"].id,
        updater_role=UserRole.EMPLOYER
    )
    assert result.status == AppStatus.INTERVIEW


def test_tc1_2_employer_a_cannot_update_employer_b_job(setup_nv3):
    """TC1.2: EMPLOYER A cập nhật hồ sơ thuộc job của EMPLOYER B → ValidationError"""
    d = setup_nv3
    with pytest.raises(ValidationError, match="Bạn không có quyền cập nhật hồ sơ này!"):
        update_application_status(
            app_id=d["app_b"].id,
            new_status="INTERVIEW",
            updater_id=d["employer_a"].id,
            updater_role=UserRole.EMPLOYER
        )


def test_tc1_3_candidate_cannot_update(setup_nv3):
    """TC1.3: CANDIDATE gọi hàm cập nhật trạng thái → ValidationError"""
    d = setup_nv3
    with pytest.raises(ValidationError, match="Bạn không có quyền cập nhật hồ sơ!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="INTERVIEW",
            updater_id=d["candidate_a"].id,
            updater_role=UserRole.CANDIDATE
        )


def test_tc1_4_admin_updates_any_app(setup_nv3):
    """TC1.4: ADMIN cập nhật hồ sơ bất kỳ (không phải job của mình) → Thành công"""
    d = setup_nv3
    result = update_application_status(
        app_id=d["app_b"].id,
        new_status="INTERVIEW",
        updater_id=d["admin"].id,
        updater_role=UserRole.ADMIN
    )
    assert result.status == AppStatus.INTERVIEW


def test_tc1_5_applications_isolation(setup_nv3):
    """TC1.5: get_applications_by_job chỉ trả về hồ sơ thuộc đúng job đó"""
    d = setup_nv3
    apps_a = get_applications_by_job(d["job_a"].id)
    apps_b = get_applications_by_job(d["job_b"].id)

    assert all(a.job_id == d["job_a"].id for a in apps_a)
    assert all(a.job_id == d["job_b"].id for a in apps_b)
    assert d["app_b"] not in apps_a
    assert d["app_a"] not in apps_b


# ===== Nhóm 2: Kiểm tra chuyển trạng thái hợp lệ (ràng buộc b, e) =====

def test_tc2_1_submitted_to_interview(setup_nv3):
    """TC2.1: SUBMITTED → INTERVIEW → Thành công, status == INTERVIEW"""
    d = setup_nv3
    result = update_application_status(
        app_id=d["app_a"].id,
        new_status="INTERVIEW",
        updater_id=d["employer_a"].id,
        updater_role=UserRole.EMPLOYER
    )
    assert result.status == AppStatus.INTERVIEW


def test_tc2_2_submitted_to_rejected(setup_nv3):
    """TC2.2: SUBMITTED → REJECTED → Thành công, status == REJECTED"""
    d = setup_nv3
    result = update_application_status(
        app_id=d["app_a"].id,
        new_status="REJECTED",
        updater_id=d["employer_a"].id,
        updater_role=UserRole.EMPLOYER
    )
    assert result.status == AppStatus.REJECTED


def test_tc2_3_interview_to_accepted(setup_nv3, test_session):
    """TC2.3: INTERVIEW → ACCEPTED → Thành công, status == ACCEPTED"""
    d = setup_nv3
    d["app_a"].status = AppStatus.INTERVIEW
    test_session.commit()

    result = update_application_status(
        app_id=d["app_a"].id,
        new_status="ACCEPTED",
        updater_id=d["employer_a"].id,
        updater_role=UserRole.EMPLOYER
    )
    assert result.status == AppStatus.ACCEPTED


def test_tc2_4_interview_to_rejected(setup_nv3, test_session):
    """TC2.4: INTERVIEW → REJECTED → Thành công, status == REJECTED"""
    d = setup_nv3
    d["app_a"].status = AppStatus.INTERVIEW
    test_session.commit()

    result = update_application_status(
        app_id=d["app_a"].id,
        new_status="REJECTED",
        updater_id=d["employer_a"].id,
        updater_role=UserRole.EMPLOYER
    )
    assert result.status == AppStatus.REJECTED


# ===== Nhóm 3: Kiểm tra chuyển trạng thái không hợp lệ (ràng buộc c, d, e) =====

def test_tc3_1_submitted_to_accepted(setup_nv3):
    """TC3.1: SUBMITTED → ACCEPTED (bỏ qua Interview) → ValidationError (ràng buộc e)"""
    d = setup_nv3
    with pytest.raises(ValidationError, match="Phải chuyển qua trạng thái Phỏng vấn trước!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="ACCEPTED",
            updater_id=d["employer_a"].id,
            updater_role=UserRole.EMPLOYER
        )


def test_tc3_2_rejected_to_interview(setup_nv3, test_session):
    """TC3.2: REJECTED → INTERVIEW → ValidationError (ràng buộc c)"""
    d = setup_nv3
    d["app_a"].status = AppStatus.REJECTED
    test_session.commit()

    with pytest.raises(ValidationError, match="Không thể chuyển từ Từ chối sang Phỏng vấn!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="INTERVIEW",
            updater_id=d["employer_a"].id,
            updater_role=UserRole.EMPLOYER
        )


def test_tc3_3_rejected_to_submitted(setup_nv3, test_session):
    """TC3.3: REJECTED → SUBMITTED → ValidationError (ràng buộc d)"""
    d = setup_nv3
    d["app_a"].status = AppStatus.REJECTED
    test_session.commit()

    with pytest.raises(ValidationError, match="Hồ sơ đã ở trạng thái cuối, không thể thay đổi!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="SUBMITTED",
            updater_id=d["employer_a"].id,
            updater_role=UserRole.EMPLOYER
        )


def test_tc3_4_rejected_to_accepted(setup_nv3, test_session):
    """TC3.4: REJECTED → ACCEPTED → ValidationError (ràng buộc d)"""
    d = setup_nv3
    d["app_a"].status = AppStatus.REJECTED
    test_session.commit()

    with pytest.raises(ValidationError, match="Hồ sơ đã ở trạng thái cuối, không thể thay đổi!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="ACCEPTED",
            updater_id=d["employer_a"].id,
            updater_role=UserRole.EMPLOYER
        )


def test_tc3_5_accepted_to_submitted(setup_nv3, test_session):
    """TC3.5: ACCEPTED → SUBMITTED → ValidationError (ràng buộc d)"""
    d = setup_nv3
    d["app_a"].status = AppStatus.ACCEPTED
    test_session.commit()

    with pytest.raises(ValidationError, match="Hồ sơ đã ở trạng thái cuối, không thể thay đổi!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="SUBMITTED",
            updater_id=d["employer_a"].id,
            updater_role=UserRole.EMPLOYER
        )


def test_tc3_6_accepted_to_interview(setup_nv3, test_session):
    """TC3.6: ACCEPTED → INTERVIEW → ValidationError (ràng buộc d)"""
    d = setup_nv3
    d["app_a"].status = AppStatus.ACCEPTED
    test_session.commit()

    with pytest.raises(ValidationError, match="Hồ sơ đã ở trạng thái cuối, không thể thay đổi!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="INTERVIEW",
            updater_id=d["employer_a"].id,
            updater_role=UserRole.EMPLOYER
        )


def test_tc3_7_accepted_to_rejected(setup_nv3, test_session):
    """TC3.7: ACCEPTED → REJECTED → ValidationError (ràng buộc d)"""
    d = setup_nv3
    d["app_a"].status = AppStatus.ACCEPTED
    test_session.commit()

    with pytest.raises(ValidationError, match="Hồ sơ đã ở trạng thái cuối, không thể thay đổi!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="REJECTED",
            updater_id=d["employer_a"].id,
            updater_role=UserRole.EMPLOYER
        )


# ===== Nhóm 4: Kiểm tra điều kiện job (ràng buộc f) =====

def test_tc4_1_hidden_job_can_still_update(setup_nv3, test_session):
    """TC4.1: Job đã đóng (active=False) nhưng hồ sơ đã nộp trước đó → vẫn được cập nhật trạng thái"""
    d = setup_nv3
    d["job_a"].active = False
    test_session.commit()

    result = update_application_status(
        app_id=d["app_a"].id,
        new_status="INTERVIEW",
        updater_id=d["employer_a"].id,
        updater_role=UserRole.EMPLOYER
    )
    assert result.status == AppStatus.INTERVIEW


def test_tc4_2_deleted_job(setup_nv3, test_session):
    """TC4.2: Job đã bị xóa khỏi DB → ValidationError"""
    d = setup_nv3
    app_id = d["app_a"].id
    employer_id = d["employer_a"].id
    job_id = d["job_a"].id
    # Xóa trực tiếp bằng raw SQL để bypass ORM cascade (tránh set job_id=NULL)
    test_session.execute(text("DELETE FROM job WHERE id = :id"), {"id": job_id})
    test_session.commit()

    with pytest.raises(ValidationError, match="Không thể cập nhật — tin tuyển dụng không còn tồn tại!"):
        update_application_status(
            app_id=app_id,
            new_status="INTERVIEW",
            updater_id=employer_id,
            updater_role=UserRole.EMPLOYER
        )


# ===== Nhóm 5: Kiểm tra quyền xem ứng viên (ràng buộc g) =====

def test_tc5_1_candidate_sees_only_own_applications(setup_nv3):
    """TC5.1: CANDIDATE A xem /my-applications → chỉ thấy hồ sơ của A, không thấy của B"""
    d = setup_nv3
    my_apps = get_my_applications(d["candidate_a"].id)

    assert all(a.candidate_id == d["candidate_a"].id for a in my_apps)
    assert d["app_b"] not in my_apps


def test_tc5_2_candidate_cannot_update_status(setup_nv3):
    """TC5.2: CANDIDATE truy cập cập nhật trạng thái → ValidationError (không thấy danh sách job)"""
    d = setup_nv3
    with pytest.raises(ValidationError, match="Bạn không có quyền cập nhật hồ sơ!"):
        update_application_status(
            app_id=d["app_a"].id,
            new_status="INTERVIEW",
            updater_id=d["candidate_a"].id,
            updater_role=UserRole.CANDIDATE
        )
