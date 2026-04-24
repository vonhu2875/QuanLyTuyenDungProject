import hashlib
import io
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest

from rapp import db
from rapp.dao import add_application, get_job_by_id
from rapp.exceptions import ValidationError, DuplicateError
from rapp.models import User, UserRole, Category, Job, Application
from rapp.test.test_base import create_app


# ───────────────────────── helpers ──────────────────────────

def _pwd(raw='123456'):
    return hashlib.md5(raw.encode()).hexdigest()


def _make_pdf():
    """Bytes PDF hợp lệ không có mật khẩu."""
    return b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF'


def _make_encrypted_pdf():
    """Bytes PDF chứa marker /Encrypt (giả lập PDF có mật khẩu)."""
    return b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\n2 0 obj\n<< /Encrypt << /Filter /Standard >> >>\n%%EOF'


def _mock_cv(filename, content=None):
    """Tạo mock FileStorage object."""
    cv = MagicMock()
    cv.filename = filename
    cv.read.return_value = content if content is not None else _make_pdf()
    return cv


# ───────────────────────── fixtures ─────────────────────────

@pytest.fixture
def app_nv3():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def session_nv3(app_nv3):
    yield db.session
    db.session.rollback()


@pytest.fixture
def sample_data(session_nv3):
    cat = Category(name='CNTT')
    session_nv3.add(cat)
    session_nv3.flush()

    employer = User(name='Công ty ABC', username='employer_t', password=_pwd(),
                    user_role=UserRole.EMPLOYER, phone='0100000001', email='emp_t@test.com')
    candidate = User(name='Ứng viên A', username='candidate_t', password=_pwd(),
                     user_role=UserRole.CANDIDATE, phone='0100000002', email='cand_t@test.com')
    session_nv3.add_all([employer, candidate])
    session_nv3.flush()

    job = Job(title='Lập trình viên Python Flask',
              description='Yêu cầu 1 năm kinh nghiệm Python.',
              salary=15_000_000,
              deadline=datetime.now() + timedelta(days=30),
              category_id=cat.id,
              employer_id=employer.id)
    session_nv3.add(job)
    session_nv3.commit()

    return {'employer': employer, 'candidate': candidate, 'job': job}


# ─────────── Nhóm 1: Kiểm tra quyền truy cập ───────────────

# TC1.1 — EMPLOYER không thấy nút "Nộp hồ sơ" được kiểm soát ở template;
#          ở tầng dao, EMPLOYER bị từ chối với ValidationError.
def test_tc1_1_employer_cannot_apply(app_nv3, sample_data):
    """TC1.1 — EMPLOYER bị từ chối nộp hồ sơ."""
    mock_user = MagicMock()
    mock_user.user_role = UserRole.EMPLOYER
    mock_user.id = sample_data['employer'].id

    with patch('rapp.dao.current_user', mock_user):
        with pytest.raises(ValidationError) as exc:
            add_application(
                job_id=sample_data['job'].id,
                cv_file=_mock_cv('cv.pdf')
            )
    assert "không có quyền" in str(exc.value)


# TC1.2 — Route POST /jobs/<id>/apply có @login_required;
#          kiểm tra gián tiếp qua dao: nếu không phải CANDIDATE → ValidationError.
#          (Redirect thực sự được xử lý bởi Flask-Login @login_required trên route)
def test_tc1_2_admin_cannot_apply(app_nv3, sample_data):
    """TC1.2 — ADMIN cũng bị từ chối như người chưa đăng nhập đúng vai trò."""
    mock_user = MagicMock()
    mock_user.user_role = UserRole.ADMIN
    mock_user.id = 999

    with patch('rapp.dao.current_user', mock_user):
        with pytest.raises(ValidationError) as exc:
            add_application(
                job_id=sample_data['job'].id,
                cv_file=_mock_cv('cv.pdf')
            )
    assert "không có quyền" in str(exc.value)


# ─────────── Nhóm 2: Kiểm tra định dạng file CV ────────────

def test_tc2_1_valid_pdf_success(app_nv3, sample_data):
    """TC2.1 — Nộp file .pdf hợp lệ → tạo Application thành công."""
    mock_user = MagicMock()
    mock_user.user_role = UserRole.CANDIDATE
    mock_user.id = sample_data['candidate'].id

    with patch('rapp.dao.current_user', mock_user):
        with patch('cloudinary.uploader.upload') as mock_upload:
            mock_upload.return_value = {'secure_url': 'https://cloudinary.com/test.pdf'}
            add_application(
                job_id=sample_data['job'].id,
                cv_file=_mock_cv('cv.pdf', _make_pdf())
            )

    record = Application.query.filter_by(
        candidate_id=sample_data['candidate'].id,
        job_id=sample_data['job'].id
    ).first()
    assert record is not None
    assert record.cv_path == 'https://cloudinary.com/test.pdf'


def test_tc2_2_non_pdf_file_rejected(app_nv3, sample_data):
    """TC2.2 — Nộp file .docx → ValidationError định dạng."""
    mock_user = MagicMock()
    mock_user.user_role = UserRole.CANDIDATE
    mock_user.id = sample_data['candidate'].id

    with patch('rapp.dao.current_user', mock_user):
        with pytest.raises(ValidationError) as exc:
            add_application(
                job_id=sample_data['job'].id,
                cv_file=_mock_cv('cv.docx', b'fake docx content')
            )
    assert ".pdf" in str(exc.value)


def test_tc2_2_xlsx_file_rejected(app_nv3, sample_data):
    """TC2.2 — Nộp file .xlsx → ValidationError định dạng."""
    mock_user = MagicMock()
    mock_user.user_role = UserRole.CANDIDATE
    mock_user.id = sample_data['candidate'].id

    with patch('rapp.dao.current_user', mock_user):
        with pytest.raises(ValidationError) as exc:
            add_application(
                job_id=sample_data['job'].id,
                cv_file=_mock_cv('cv.xlsx', b'fake xlsx content')
            )
    assert ".pdf" in str(exc.value)


def test_tc2_3_encrypted_pdf_rejected(app_nv3, sample_data):
    """TC2.3 — Nộp file PDF có mật khẩu → ValidationError."""
    mock_user = MagicMock()
    mock_user.user_role = UserRole.CANDIDATE
    mock_user.id = sample_data['candidate'].id

    with patch('rapp.dao.current_user', mock_user):
        with pytest.raises(ValidationError) as exc:
            add_application(
                job_id=sample_data['job'].id,
                cv_file=_mock_cv('cv.pdf', _make_encrypted_pdf())
            )
    assert "mật khẩu" in str(exc.value)


def test_tc2_no_file_rejected(app_nv3, sample_data):
    """Không chọn file → ValidationError."""
    mock_user = MagicMock()
    mock_user.user_role = UserRole.CANDIDATE
    mock_user.id = sample_data['candidate'].id

    empty_cv = MagicMock()
    empty_cv.filename = ''

    with patch('rapp.dao.current_user', mock_user):
        with pytest.raises(ValidationError) as exc:
            add_application(job_id=sample_data['job'].id, cv_file=empty_cv)
    assert "đính kèm" in str(exc.value)


# ─────────── Nhóm 3: Kiểm tra logic trùng hồ sơ ───────────

def test_tc3_1_duplicate_application_rejected(app_nv3, sample_data):
    """TC3.1 — Nộp hồ sơ lần 2 cùng vị trí → DuplicateError."""
    mock_user = MagicMock()
    mock_user.user_role = UserRole.CANDIDATE
    mock_user.id = sample_data['candidate'].id

    # Lần 1: thành công
    with patch('rapp.dao.current_user', mock_user):
        with patch('cloudinary.uploader.upload') as mock_upload:
            mock_upload.return_value = {'secure_url': 'https://cloudinary.com/cv1.pdf'}
            add_application(
                job_id=sample_data['job'].id,
                cv_file=_mock_cv('cv.pdf', _make_pdf())
            )

    # Lần 2: trùng → DuplicateError
    with patch('rapp.dao.current_user', mock_user):
        with patch('cloudinary.uploader.upload') as mock_upload:
            mock_upload.return_value = {'secure_url': 'https://cloudinary.com/cv2.pdf'}
            with pytest.raises(DuplicateError) as exc:
                add_application(
                    job_id=sample_data['job'].id,
                    cv_file=_mock_cv('cv2.pdf', _make_pdf())
                )
    assert "1 hồ sơ" in str(exc.value)


# ─────────── Kiểm tra get_job_by_id ────────────────────────

def test_get_job_by_id_found(app_nv3, sample_data):
    """get_job_by_id trả về đúng job khi tồn tại."""
    job = get_job_by_id(sample_data['job'].id)
    assert job is not None
    assert job.title == sample_data['job'].title


def test_get_job_by_id_not_found(app_nv3, sample_data):
    """get_job_by_id trả về None khi không tồn tại."""
    job = get_job_by_id(99999)
    assert job is None
