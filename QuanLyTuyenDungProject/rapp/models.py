import hashlib
from datetime import datetime, timedelta

from flask_login import UserMixin
from sqlalchemy import Column, String, Enum, Float, Text, DateTime, Integer, ForeignKey, UniqueConstraint
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
    phone = Column(String(15), nullable=False)
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

    #Tạo ràng buộc mỗi nhà tuyển dụng không được tạo trùng tiêu đề
    __table_args__=(
        UniqueConstraint('title', 'employer_id', name='unique_job_per_company'),
    )

    def __str__(self):
        return self.title



class Application(BaseModel):
    cv_path = Column(String(255), nullable=False)
    status = Column(Enum(AppStatus), default=AppStatus.SUBMITTED)
    feedback = Column(Text, nullable=True)
    job_id = Column(Integer, ForeignKey(Job.id), nullable=False)
    candidate_id = Column(Integer, ForeignKey(User.id), nullable=False)

    #Tạo ràng buộc mỗi ứng viên chỉ được ứng tuyển 1 hồ sơ cho 1 vị trí duy nhất
    __table_args__ = (
        UniqueConstraint('candidate_id', 'job_id', name='unique_application'),
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        c1 = Category(name="Công nghệ thông tin")
        c2 = Category(name="Marketing")
        c3 = Category(name="Kế toán")
        c4 = Category(name="Ngôn ngữ Anh")
        db.session.add_all([c1, c2, c3, c4])

        password = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())
        admin = User(
            name="Quản trị viên",
            username="admin",
            password=password,
            user_role=UserRole.ADMIN,
            phone="0123456789",
            email="admin@gmail.com"
        )
        db.session.add(admin)

        emp1 = User(name='Công ty Công nghệ ABC',
                   username='employer1',
                   password=password,
                   user_role=UserRole.EMPLOYER,
                   phone="0123456789",
                   email="employer1@gmail.com")

        emp2 = User(name='Công ty Công nghệ XYZ',
                   username='employer2',
                   password=password,
                   user_role=UserRole.EMPLOYER,
                   phone="0123456789",
                   email="employer2@gmail.com")


        db.session.add_all([emp1, emp2])
        db.session.commit()

        now = datetime.now()
        j1 = Job(title='Lập trình viên Python (Flask/Django)',
                 description='Phát triển hệ thống Backend, yêu cầu 1 năm kinh nghiệm Python.',
                 salary=15000000,
                 deadline= now+timedelta(days=15),
                 category_id=c1.id,
                 employer_id=emp1.id)

        j2 = Job(title='Chuyên viên Phân tích Dữ liệu',
                 description='Sử dụng SQL, Python để phân tích dữ liệu kinh doanh.',
                 salary=20000000,
                 deadline=now + timedelta(days=20),
                 category_id=c1.id,
                 employer_id=emp2.id)

        j3 = Job(title='Kế toán tổng hợp',
                 description='Thực hiện báo cáo thuế, quản lý sổ sách chứng từ.',
                 salary=12000000,
                 deadline=now + timedelta(days=21),
                 category_id=c3.id,
                 employer_id=emp2.id)

        j4 = Job(title='Content Creator (TikTok/Facebook)',
                 description='Sáng tạo nội dung video, quản lý Fanpage công ty.',
                 salary=10000000,
                 deadline=now + timedelta(days=35),
                 category_id=c2.id,
                 employer_id=emp1.id)

        j5 = Job(title='Biên dịch viên tiếng Anh',
                 description='Dịch thuật các tài liệu kỹ thuật và hợp đồng kinh tế.',
                 salary=18000000,
                 deadline=now + timedelta(days=15),
                 category_id=c4.id,
                 employer_id=emp1.id)

        db.session.add_all([j1, j2, j3, j4, j5])
        db.session.commit()

        db.session.commit()
