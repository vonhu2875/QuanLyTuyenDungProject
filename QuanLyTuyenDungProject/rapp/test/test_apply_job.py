from unittest.mock import patch

import pytest
import io
from datetime import datetime, timedelta
from rapp.dao import apply_for_job
from rapp.exceptions import ValidationError, DuplicateError
from rapp.models import UserRole, Job, Application
from rapp.test.test_base import test_session, test_app, job_to_apply, sample_category, sample_employer, sample_candidate

def create_mock_file(filename, content=b"fake content", size=None):
    if size:
        # Nếu test dung lượng lớn, vẫn phải đảm bảo 4 byte đầu là %PDF
        content = b"%PDF" + b"0" * (size - 4)
    file = io.BytesIO(content)
    file.filename = filename
    return file


# 1. Test nộp thành công
def test_apply_success(test_session, job_to_apply, sample_candidate):
    cv = create_mock_file("my_cv.pdf", content=b"%PDF-1.5 test content")

    with patch('cloudinary.uploader.upload') as mock_upload:
        mock_upload.return_value = {
            'secure_url': 'https://res.cloudinary.com/demo/image/upload/sample_cv.pdf'
        }

        app = apply_for_job(
            job_id=job_to_apply.id,
            candidate_id=sample_candidate.id,
            user_role=UserRole.CANDIDATE,
            cv_file=cv
        )

        assert app is not None
        assert app.cv_path == 'https://res.cloudinary.com/demo/image/upload/sample_cv.pdf'
        assert app.job_id == job_to_apply.id

# 2. Test sai vai trò (Nhà tuyển dụng nộp hồ sơ)
def test_apply_invalid_role(test_session, job_to_apply, sample_employer):
    cv = create_mock_file("my_cv.pdf", content=b"%PDF-1.5 test content")

    with pytest.raises(ValidationError, match="Chỉ Ứng viên mới có quyền nộp hồ sơ!"):
        apply_for_job(
            job_id=job_to_apply.id,
            candidate_id=sample_employer.id,
            user_role=sample_employer.user_role,
            cv_file=cv
        )

# 3. Test sai định dạng file
def test_apply_invalid_file_type(test_session, job_to_apply, sample_candidate):
    cv = create_mock_file("my_cv.jpg", content=b"%PDF-1.5 test content")

    with pytest.raises(ValidationError, match="Hệ thống chỉ chấp nhận file định dạng .pdf"):
        apply_for_job(
            job_id=job_to_apply.id,
            candidate_id=sample_candidate.id,
            user_role=sample_candidate.user_role,
            cv_file=cv
        )


# 4. Test file quá dung lợng
def test_apply_file_too_large(test_session, job_to_apply, sample_candidate):
    # b"%PDF" chiếm 4 byte, cộng với chuỗi số 0 cho đủ dung lượng
    large_content = b"%PDF" + b"0" * (11 * 1024 * 1024 - 4)
    cv = create_mock_file("big_cv.pdf", content=large_content)

    with pytest.raises(ValidationError, match="Dung lượng file CV tối đa là 10MB!"):
        apply_for_job(
            job_id=job_to_apply.id,
            candidate_id=sample_candidate.id,
            user_role=sample_candidate.user_role,
            cv_file=cv
        )


# 5. Test file nộp trùng
def test_apply_duplicate(test_session, job_to_apply, sample_candidate):
    cv = create_mock_file("my_cv.pdf", content=b"%PDF-1.5 test content")

    with patch('cloudinary.uploader.upload') as mock_upload:
        mock_upload.return_value = {'secure_url': 'https://link-cv.pdf'}

        # Nộp lần 1 thành công
        apply_for_job(job_to_apply.id, sample_candidate.id, sample_candidate.user_role, cv)

        # Nộp lần 2 (cùng job_id và candidate_id)
        with pytest.raises(DuplicateError, match="Bạn đã nộp hồ sơ cho công việc này rồi!"):
            apply_for_job(job_to_apply.id, sample_candidate.id, sample_candidate.user_role, cv)


# 6. Test tin đã đóng
def test_apply_job_inactive(test_session, job_to_apply, sample_candidate):
    cv = create_mock_file("my_cv.pdf", content=b"%PDF-1.5 test content")
    # Chuyển trạng thái job sang đóng
    job_to_apply.active = False
    test_session.commit()

    with pytest.raises(ValidationError, match="Tin tuyển dụng này đã đóng hoặc không còn tồn tại!"):
        apply_for_job(
            job_id=job_to_apply.id,
            candidate_id=sample_candidate.id,
            user_role=sample_candidate.user_role,
            cv_file=cv
        )


# 7. Test tin hết hạn (Deadline < Now)
def test_apply_job_expired(test_session, job_to_apply, sample_candidate):
    cv = create_mock_file("my_cv.pdf", content=b"%PDF-1.5 test content")
    # Chỉnh deadline về quá khứ
    job_to_apply.deadline = datetime.now() - timedelta(days=1)
    test_session.commit()

    with pytest.raises(ValidationError, match="Đã hết hạn nộp hồ sơ!"):
        apply_for_job(
            job_id=job_to_apply.id,
            candidate_id=sample_candidate.id,
            user_role=sample_candidate.user_role,
            cv_file=cv
        )


# 8. Test lỗi: Tên file hợp lệ nhưng nội dung file trống (0 byte)
def test_apply_empty_file(test_session, job_to_apply, sample_candidate):
    cv = create_mock_file("empty.pdf", content=b"")

    with pytest.raises(ValidationError, match="File CV không được để trống!"):
        apply_for_job(job_to_apply.id, sample_candidate.id, sample_candidate.user_role, cv)


# 9. Test lỗi: Lỗi phát sinh từ phía Cloudinary
def test_apply_cloudinary_error(test_session, job_to_apply, sample_candidate):
    cv = create_mock_file("my_cv.pdf", content=b"%PDF-1.5 test content")

    with patch('cloudinary.uploader.upload') as mock_upload:
        mock_upload.side_effect = Exception("Cloudinary connection failed")

        with pytest.raises(Exception, match="Lỗi hệ thống: Cloudinary connection failed"):
            apply_for_job(job_to_apply.id, sample_candidate.id, sample_candidate.user_role, cv)

        exists = Application.query.filter_by(job_id=job_to_apply.id).first()
        assert exists is None


# 10. Test file giả
def test_apply_spoofed_file(test_session, job_to_apply, sample_candidate):
    fake_content = b"This is just a normal text file, not a real PDF structure"
    cv = create_mock_file("fake_cv.pdf", content=fake_content)

    with pytest.raises(ValidationError, match="Nội dung file không phải là PDF hợp lệ!"):
        apply_for_job(
            job_id=job_to_apply.id,
            candidate_id=sample_candidate.id,
            user_role=sample_candidate.user_role,
            cv_file=cv
        )


# 11. Test lỗi: File có ký tự đặc biệt trong tên
def test_apply_filename_special_chars(test_session, job_to_apply, sample_candidate):
    special_name = "CV_Nguyễn Văn Hà_#@!$%^&*().pdf"
    cv = create_mock_file(special_name, content=b"%PDF-1.5 test content")

    with patch('cloudinary.uploader.upload') as mock_upload:
        mock_upload.return_value = {'secure_url': 'https://link-cv.pdf'}

        app = apply_for_job(
            job_id=job_to_apply.id,
            candidate_id=sample_candidate.id,
            user_role=sample_candidate.user_role,
            cv_file=cv
        )
        assert app is not None
        assert app.job_id == job_to_apply.id

# 12. Test lỗi: Up lên Cloudinary thành công nhưng khi lưu xuống Database lỗi
def test_apply_database_commit_error(test_session, job_to_apply, sample_candidate):
    cv = create_mock_file("my_cv.pdf", content=b"%PDF-1.5")

    with patch('cloudinary.uploader.upload') as mock_upload, \
            patch('rapp.db.session.commit') as mock_commit:
        mock_upload.return_value = {'secure_url': 'https://link.pdf'}
        # Giả lập lỗi khi commit vào database
        mock_commit.side_effect = Exception("Database is down")

        with pytest.raises(Exception, match="Lỗi hệ thống"):
            apply_for_job(job_to_apply.id, sample_candidate.id, sample_candidate.user_role, cv)

# 13. Nộp hồ sơ vào giấy cuối
def test_apply_exactly_at_deadline(test_session, job_to_apply, sample_candidate):
    job_to_apply.deadline = datetime.now() - timedelta(seconds=1)
    test_session.commit()

    cv = create_mock_file("cv.pdf", content=b"%PDF-1.5")
    with pytest.raises(ValidationError, match="Đã hết hạn nộp hồ sơ!"):
        apply_for_job(job_to_apply.id, sample_candidate.id, sample_candidate.user_role, cv)

#14. Test lỗi: candidate nộp job không tồn tại
def test_apply_non_existent_job(test_session, sample_candidate):
    cv = create_mock_file("cv.pdf", content=b"%PDF-1.5")
    invalid_job_id = 999999

    with pytest.raises(ValidationError, match="Tin tuyển dụng không tồn tại!"):
        apply_for_job(invalid_job_id, sample_candidate.id, sample_candidate.user_role, cv)
