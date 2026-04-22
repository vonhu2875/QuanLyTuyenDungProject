import hashlib
from datetime import datetime, timedelta
from sqlite3 import IntegrityError

import unicodedata
from flask_login import current_user
from sqlalchemy import func

from rapp.models import Category, Job, User, UserRole
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
        raise Exception("Username đã tồn tại!")
    return u

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
    if not username:
        raise ValidationError("Vui lòng nhập username!")
    if not password:
        raise ValidationError("Vui lòng nhập mật khẩu!")
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User.query.filter(User.username == username, User.password == password).first()
    if not u.active:
        return None
    return u