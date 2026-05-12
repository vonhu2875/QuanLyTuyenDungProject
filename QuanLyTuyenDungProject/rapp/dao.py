import hashlib
import os
from datetime import datetime, timedelta
from sqlite3 import IntegrityError

import unicodedata
from sqlalchemy import func

from rapp.models import Category, Job, User, UserRole, Application, AppStatus
from flask import current_app
import cloudinary.uploader
from rapp import db
from rapp.exceptions import ValidationError, DuplicateError
import re


def get_user_by_id(user_id):
    return User.query.get(user_id)

def load_categories():
    return Category.query.all()

def normalize(text=None):
    text = text.strip().lower()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    return text

def update_active_job():
    expired_jobs = Job.query.filter(Job.active == True, Job.deadline < datetime.now()).all()
    for job in expired_jobs:
        job.active = False
    db.session.commit()

def load_jobs(cate_id=None, kw=None, page=None):
    update_active_job()
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

    # Kiểm tra username
    if len(username) < 5 or len(username) > 20:
        raise ValidationError("Username phải từ 5 đến 20 ký tự!")

    # \s thay vì chỉ để [ ] là để thay cho cả khoảng trắng, các dấu tab xuống dòng
    if re.search(r'\s', username):
        raise ValidationError("Username không được chứa khoảng trắng!")

    if not re.match(r'^[a-zA-Z0-9]+$', username):
        raise  ValidationError("Username không được chứa ký tự đặc biệt")

    # Kiểm tra password
    if len(password) < 8:
        raise ValidationError('Password phải ít nhất 8 ký tự')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password phải chứa số')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password phải chứa ký tự hoa')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password phải chứa ký tự')
    #Kiểm tra email
    email_regrex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regrex, email):
        raise ValidationError("Email không đúng định dạng!")

    #Kiểm tra name
    if not name or not name.strip():
        raise ValidationError("Vui lòng nhập tên!")
    if len(name) > 255:
        raise ValidationError("Tên không được quá 255 ký tự!")

    #Kiểm tra user_role
    if user_role is None:
        raise ValidationError("Vai trò không được để trống!")

    if user_role not in [UserRole.EMPLOYER, UserRole.CANDIDATE]:
        raise ValidationError("Vai trò không hợp lệ")

    #Kiểm tra sdt
    if phone is None:
        raise ValidationError("Bắt buộc nhập số điện thoại!")

    if len(phone) > 15:
        raise ValidationError("Số điện thoại chỉ được nhập tối đa 15 ký tự")

    if not re.match(r'^[0-9]+$', phone):
        raise ValidationError("Số điện thoại không hợp lệ!")

    #Kiểm tra phía dưới db username
    if User.query.filter(User.username.__eq__(username)).first():
        raise DuplicateError(f'Username {username} đã tồn tại')

    # Kiểm tra phía dưới db email
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
        raise Exception("Không thể thêm user!")
    return u

def _validate_job_fields(title, salary, deadline):
    if not title:
        raise ValidationError("Phải có tiêu đề!")
    title = title.strip()
    if len(title) < 10:
        raise ValidationError("Tiêu đề phải tối thiểu 10 ký tự!")
    if len(title) > 255:
        raise ValidationError("Tiêu đề chỉ tối đa 255 ký tự!")
    try:
        salary = float(salary)
    except (ValueError, TypeError):
        raise ValidationError("Lương phải là số")
    if salary <= 0:
        raise ValidationError("Lương phải > 0!")
    now = datetime.now()
    if deadline < now:
        raise ValidationError("Deadline phải lớn hơn ngày tháng năm hiện tại!")
    if deadline > now + timedelta(days=365):
        raise ValidationError("Hạn deadline chỉ tối đa 1 năm kể từ ngày tạo tin!")
    deadline = deadline.replace(hour=23, minute=59, second=59)
    return title, salary, deadline

def add_job(title, description, salary, deadline, category_id, employer_id, user_role):
    if user_role not in [UserRole.EMPLOYER, UserRole.ADMIN]:
        raise ValidationError("Bạn không có quyền đăng tin!")
    title, salary, deadline = _validate_job_fields(title, salary, deadline)
    if Job.query.filter(func.lower(Job.title)==title.lower(), Job.employer_id == employer_id).first():
        raise DuplicateError("Tin tuyển dụng đã tồn tại!")
    j = Job(title=title, description=description, salary=salary, deadline=deadline, category_id=category_id, employer_id=employer_id)
    db.session.add(j)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("Không thể tải Job lên!")
    return j

def auth_user(username, password):
    if not username:
        raise ValidationError("Vui lòng nhập username!")
    if not password:
        raise ValidationError("Vui lòng nhập mật khẩu!")
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User.query.filter(User.username == username).first()
    if not u:
        raise ValidationError("Sai tên đăng nhập hoặc sai mật khẩu!")
    if password != u.password:
        raise ValidationError("Sai tên đăng nhập hoặc sai mật khẩu!")
    if not u.active:
        raise ValidationError("Tài khoản người dùng không tồn tại!")
    return u


#=========================Nghiệp vụ 2: Ngại và Hiền (Bé Hà)==========================


def apply_for_job(job_id, candidate_id, user_role, cv_file):
    # 1. Kiểm tra quyền và đăng nhập
    if not candidate_id:
        raise ValidationError("Bạn cần đăng nhập để nộp hồ sơ!")
    if user_role != UserRole.CANDIDATE:
        raise ValidationError("Chỉ Ứng viên mới có quyền nộp hồ sơ!")

    # 2. Kiểm tra tin tuyển dụng
    job = db.session.get(Job, job_id)
    if not job:
        raise ValidationError("Tin tuyển dụng không tồn tại!")

    # RÀNG BUỘC: Không nộp sau hạn hoặc tin đã đóng thủ công
    if not job.active:
        raise ValidationError("Tin tuyển dụng này đã đóng hoặc không còn tồn tại!")
    if job.deadline < datetime.now():
        raise ValidationError("Đã hết hạn nộp hồ sơ!")

    # 3. Kiểm tra nộp trùng (1 hồ sơ / 1 vị trí)
    exists = Application.query.filter_by(job_id=job_id, candidate_id=candidate_id).first()
    if exists:
        raise DuplicateError("Bạn đã nộp hồ sơ cho công việc này rồi!")

    # 4. Kiểm tra file CV
    if not cv_file or cv_file.filename == '':
        raise ValidationError("Vui lòng tải lên CV của bạn!")

    # Kiểm tra nội dung thực
    header = cv_file.read(4)  # Đọc 4 byte đầu tiên
    cv_file.seek(0)  # Reset con trỏ file ngay lập tức

    # Kiểm tra dung lượng (0 < size <= 10MB)
    blob = cv_file.read()
    size = len(blob)
    cv_file.seek(0)  # Reset con trỏ file sau khi read

    if size <= 0:
        raise ValidationError("File CV không được để trống!")
    if size > 10 * 1024 * 1024:  # 10MB
        raise ValidationError("Dung lượng file CV tối đa là 10MB!")

    # Kiểm tra đuôi file (Chỉ nhận .pdf)
    ext = os.path.splitext(cv_file.filename)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Hệ thống chỉ chấp nhận file định dạng .pdf (Word, Excel... sẽ bị từ chối)!")

    # %PDF tương ứng với b'\x25\x50\x44\x46'
    if header != b'%PDF':
        raise ValidationError("Nội dung file không phải là PDF hợp lệ!")

    # 5. Lưu hồ sơ
    try:
        res = cloudinary.uploader.upload(cv_file)
        cv_path = res['secure_url']

        new_app = Application(
            job_id=job_id,
            candidate_id=candidate_id,
            cv_path=cv_path
        )
        db.session.add(new_app)
        db.session.commit()
        return new_app
    except Exception as e:
        db.session.rollback()
        raise Exception("Lỗi hệ thống: " + str(e))

def get_job_by_id(job_id):
    return Job.query.get(job_id)

def check_applied(candidate_id, job_id):
    from rapp.models import Application
    return (Application.query
                        .filter_by(candidate_id=candidate_id, job_id=job_id)
                        .first() is not None)

def update_user_profile(user_id, data):
    user = User.query.get(user_id)
    if user:
        user.name = data.get('name')
        user.email = data.get('email')
        user.phone = data.get('phone')

        db.session.commit()
        return True
    return False

def get_my_applications(candidate_id):
    return Application.query.filter_by(candidate_id=candidate_id).all()


#=========================Nghiệp vụ 3: Đẹp trai có gì sai (Nhu Toàn )==========================
def get_application_by_id(app_id):
    return Application.query.get(app_id)

def get_applications_by_job(job_id):
    return Application.query.filter_by(job_id=job_id).all()

def get_apps_by_employer(employer_id, user_role):
    if user_role == UserRole.ADMIN:
        jobs = Job.query.all()
    else:
        jobs = Job.query.filter_by(employer_id=employer_id).all()
    return {job: Application.query.filter_by(job_id=job.id).all() for job in jobs}

def _check_update_permission(updater_role, updater_id, job):
    if updater_role not in [UserRole.EMPLOYER, UserRole.ADMIN]:
        raise ValidationError("Bạn không có quyền cập nhật hồ sơ!")
    if not job:
        raise ValidationError("Không thể cập nhật — tin tuyển dụng không còn tồn tại!")
    if not job.active:
        raise ValidationError("Không thể cập nhật — tin tuyển dụng không còn hoạt động!")
    if updater_role == UserRole.EMPLOYER and job.employer_id != updater_id:
        raise ValidationError("Bạn không có quyền cập nhật hồ sơ này!")

def _validate_status_transition(current_status, new_status):
    if current_status == AppStatus.SUBMITTED and new_status == AppStatus.ACCEPTED:
        raise ValidationError("Phải chuyển qua trạng thái Phỏng vấn trước!")
    if current_status == AppStatus.REJECTED and new_status == AppStatus.INTERVIEW:
        raise ValidationError("Không thể chuyển từ Từ chối sang Phỏng vấn!")
    if current_status in [AppStatus.ACCEPTED, AppStatus.REJECTED]:
        raise ValidationError("Hồ sơ đã ở trạng thái cuối, không thể thay đổi!")

def update_application_status(app_id, new_status, updater_id, updater_role):
    application = Application.query.get(app_id)
    if not application:
        raise ValidationError("Hồ sơ không tồn tại!")

    job = Job.query.get(application.job_id)
    _check_update_permission(updater_role, updater_id, job)

    if isinstance(new_status, str):
        try:
            new_status = AppStatus[new_status]
        except KeyError:
            raise ValidationError("Trạng thái không hợp lệ!")

    _validate_status_transition(application.status, new_status)

    application.status = new_status
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception("Lỗi hệ thống: " + str(e))
    return application


def get_categories():
    return Category.query.all()


def toggle_job_active(job_id):
    job = Job.query.get(job_id)
    if job:
        # Sử dụng cột active có sẵn trong BaseModel
        job.active = not job.active
        db.session.commit()
        return True
    return False


def update_job(job_id, data):
    job = Job.query.get(job_id)
    if not job:
        return False

    deadline_str = data.get('deadline', '').strip()
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else job.deadline

    title, salary, deadline = _validate_job_fields(data.get('title'), data.get('salary'), deadline)

    job.title = title
    job.description = data.get('description')
    job.salary = salary
    job.deadline = deadline
    job.category_id = int(data.get('category'))
    db.session.commit()
    return True

