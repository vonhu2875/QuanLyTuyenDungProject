import hashlib
import io
import re
import unicodedata
from datetime import datetime, timedelta
from sqlite3 import IntegrityError

import cloudinary.uploader
from flask import current_app
from flask_login import current_user
from sqlalchemy import func


try:
    import pypdf
    _PYPDF_AVAILABLE = True
except ImportError:
    _PYPDF_AVAILABLE = False

from rapp import db
from rapp.exceptions import DuplicateError, ValidationError
from rapp.models import Application, AppStatus, Category, Job, User, UserRole


def get_user_by_id(user_id):
    return User.query.get(user_id)


def load_categories():
    return Category.query.all()

def normalize(text=None):
    text = text.strip().lower()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    return text

def load_jobs(cate_id=None, kw=None, page=None):
    query = Job.query
    if cate_id:
        query = query.filter(Job.category_id.__eq__(cate_id))
    jobs = query.all()
    if kw and kw.strip():
        kw_norm = normalize(kw)
        filtered = []
        for j in jobs:
            if normalize(j.title).__contains__(kw_norm):
                filtered.append(j)
        jobs = filtered

    if page is not None:
        if page < 1:
            return []
        start = (page - 1) * current_app.config['PAGE_SIZE']
        jobs = jobs[start: start + current_app.config['PAGE_SIZE']]
    return jobs

def count_jobs(category_id=None):
    if category_id:
        return Job.query.filter(Job.category_id==category_id).count()
    return Job.query.count()

def add_user(name, username, password, avatar, email, phone, user_role):
    username = username.strip()
    if len(username) < 5 or len(username) > 20:
        raise ValidationError("Username phải từ 5 đến 20 ký tự!")

    # \s thay vì chỉ để [ ] là để thay cho cả khoảng trắng, các dấu tab xuống dòng
    if re.search(r'\s', username):
        raise ValidationError("Username không được chứa khoảng trắng!")

    if not re.match(r'^[a-zA-Z0-9]+$', username):
        raise  ValidationError("Username không được chứa ký tự đặc biệt")

    email_regrex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regrex, email):
        raise ValidationError("Email không đúng định dạng!")

    if not name or not name.strip():
        raise ValidationError("Vui lòng nhập tên!")
    if len(name) > 255:
        raise ValidationError("Tên không được quá 255 ký tự!")

    if user_role is None:
        raise ValidationError("Vai trò không được để trống!")

    if phone is None:
        raise ValidationError("Bắt buộc nhập số điện thoại!")

    if len(phone) > 15:
        raise ValidationError("Số điện thoại chỉ được nhập tối đa 15 ký tự")

    if not re.match(r'^[0-9]+$', phone):
        raise ValidationError("Số điện thoại không hợp lệ!")

    if User.query.filter(User.username.__eq__(username)).first():
        raise DuplicateError(f'Username {username} đã tồn tại')

    if User.query.filter(User.email.__eq__(email)).first():
        raise DuplicateError(f'Email {email} đã tồn tại')

    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name = name.strip(), username=username.strip(), password=password, email=email, phone=phone, user_role=user_role)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get("secure_url")
    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("Username đã tồn tại!")

def add_job(title, description, salary, deadline, category_id):
    if current_user.user_role not in [UserRole.EMPLOYER, UserRole.ADMIN]:
        raise ValidationError("Bạn không có quyền đăng tin!")
    title = title.strip()
    if len(title) < 10:
        raise ValidationError("Tiêu đề phải tối thiểu 10 ký tự!")
    if len(title) > 255:
        raise ValidationError("Tiêu đề chỉ tối đa 255 ký tự!")
    try:
        salary = float(salary)
    except:
        raise ValidationError("Lương phải là số")

    if salary <= 0:
        raise ValidationError("Lương phải > 0!")
    now = datetime.now()
    if deadline.date() < now.date():
        raise ValidationError("Deadline phải lớn hơn ngày tháng năm hiện tại!")
    if deadline.date() > now.date() + timedelta(days=365):
        raise ValidationError("Hạn deadline chỉ tối đa 1 năm kể từ ngày tạo tin!")
    deadline = deadline.replace(hour=23, minute=59, second=59)
    if Job.query.filter(func.lower(Job.title)==title.lower(), Job.employer_id == current_user.id).first():
        raise DuplicateError("Tin tuyển dụng đã tồn tại!")

    j = Job(title=title, description=description, salary=salary, deadline=deadline, category_id=category_id, employer_id=current_user.id)
    db.session.add(j)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("Không thể tải Job lên!")

def auth_user(username, password):
    if not password:
        raise ValidationError("Vui lòng nhập mật khẩu!")
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User.query.filter(User.username == username).first()
    if not user:
        raise ValidationError(f"Không có username {username}!")
    if user.password != password:
        raise ValidationError("Nhập mật khẩu không đúng!Vui lòng nhập lại")
    return user

#Nghiệp vụ chính 3: Nộp Hồ Sơ Ứng Tuyển

def get_job_by_id(job_id):
    return Job.query.get(job_id)


def _is_pdf_encrypted(file_bytes):
    if _PYPDF_AVAILABLE:
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            return reader.is_encrypted
        except Exception:
            return False
    return b'/Encrypt' in file_bytes


def add_application(job_id, cv_file):
    if current_user.user_role != UserRole.CANDIDATE:
        raise ValidationError("Bạn không có quyền nộp hồ sơ!")

    if not cv_file or not cv_file.filename:
        raise ValidationError("Vui lòng đính kèm file CV!")

    if not cv_file.filename.lower().endswith('.pdf'):
        raise ValidationError("Chỉ chấp nhận file định dạng .pdf!")

    file_bytes = cv_file.read()

    if _is_pdf_encrypted(file_bytes):
        raise ValidationError("File PDF không được bảo vệ bằng mật khẩu!")

    existing = Application.query.filter_by(
        candidate_id=current_user.id,
        job_id=job_id
    ).first()
    if existing:
        raise DuplicateError("Mỗi ứng viên chỉ được nộp 1 hồ sơ cho mỗi vị trí!")

    res = cloudinary.uploader.upload(io.BytesIO(file_bytes), resource_type='raw', folder='cv')
    cv_url = res.get('secure_url')

    application = Application(cv_path=cv_url, job_id=job_id, candidate_id=current_user.id)
    db.session.add(application)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise Exception("Không thể lưu hồ sơ, vui lòng thử lại!")