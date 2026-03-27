import hashlib
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, String, Enum, Float, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship

from rapp import db, app
from enum import Enum as UserEnum


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class UserRole(UserEnum):
    ADMIN = 1
    EMPLOYER = 2
    CANDIDATE = 3

class AppStatus(UserEnum):
    SUBMITTED = 1
    INTERVIEW = 2
    ACCEPTED = 3
    REJECTED = 4

class User(BaseModel, UserMixin):
    name = Column(String(255), nullable=False)
    avatar = Column(String(255), default='https://res-console.cloudinary.com/dqrfckaek/thumbnails/transform/v1/image/upload/Y19maWxsLGhfMjAwLHdfMjAw/v1/bWFpbi1zYW1wbGVfZnB6Y3Vt/template_primary')
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)
    phone = Column(String(10), nullable=False)
    email = Column(String(100), nullable=False, unique=True)

    jobs = relationship('Job', backref='employer', lazy=True)
    applications = relationship('Application', backref='candidate', lazy=True)
    def __str__(self):
        return self.name

class Category(BaseModel):
    name = Column(String(100), nullable=False, unique=True)
    jobs = relationship('Job', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Job(BaseModel):
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    salary = Column(Float, default=0, nullable=False)
    deadline = Column(DateTime, nullable=False)

    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    employer_id = Column(Integer, ForeignKey(User.id), nullable=False)
    applications = relationship('Application', backref='job', lazy=True)
    def __str__(self):
        return self.title



class Application(BaseModel):
    cv_path = Column(String(255), nullable=False)
    status = Column(Enum(AppStatus), default=AppStatus.SUBMITTED)
    feedback = Column(Text, nullable=True)
    job_id = Column(Integer, ForeignKey(Job.id), nullable=False)
    candidate_id = Column(Integer, ForeignKey(User.id), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        c1 = Category(name="Công nghệ thông tin")
        c2 = Category(name="Marketing")
        c3 = Category(name="Kế toán")
        c4 = Category(name="Ngôn ngữ Anh")
        db.session.add_all([c1, c2, c3, c4])

        admin = User(
            name="Quản trị viên",
            username="admin",
            password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
            user_role=UserRole.ADMIN,
            phone="0123456789",
            email="admin@gmail.com"
        )
        db.session.add(admin)

        db.session.commit()
