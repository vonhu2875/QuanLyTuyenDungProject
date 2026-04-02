import hashlib
from sqlite3 import IntegrityError

from rapp.models import Category, Job, User
from flask import current_app
import cloudinary.uploader
from rapp import db
from rapp.exceptions import ValidationError, DuplicateError
import re


def get_user_by_id(user_id):
    return User.query.get(user_id)


def load_categories():
    return Category.query.all()

def load_jobs(cate_id=None, kw=None, page=None):
    query = Job.query
    if cate_id:
        query = query.filter(Job.category_id.__eq__(cate_id))

    if kw:
        query = query.filter(Job.title.contains(kw))
    if page:
        start = (page - 1) * current_app.config['PAGE_SIZE']
        query = query.slice(start, start + current_app.config['PAGE_SIZE'])
    return query.all()

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

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username==username, password==password).first()