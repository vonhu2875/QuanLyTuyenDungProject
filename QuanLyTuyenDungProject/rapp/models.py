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
    #Thái hà sửa lại thuộc tính default cua avatar, đổi default thành none, để ai không up ảnh ava lên thì nó không đụng vào link,
    #còn up ảnh thì nó ghi đè link res cloudinary lên
    # avatar = Column(String(255),
    #                 default='https://res-console.cloudinary.com/dqrfckaek/thumbnails/transform/v1/image/upload/Y19maWxsLGhfMjAwLHdfMjAw/v1/bWFpbi1zYW1wbGVfZnB6Y3Vt/template_primary')
    avatar = Column(String(255),
                    default=None)

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
        #db.drop_all()

        # 1. Khởi tạo bảng
        db.create_all()

        # 2. Thêm Danh mục (Category)
        c1 = Category(name="Công nghệ thông tin")
        c2 = Category(name="Marketing")
        c3 = Category(name="Kế toán")
        c4 = Category(name="Ngôn ngữ Anh")
        c5 = Category(name="Thiết kế đồ họa")
        c6 = Category(name="Thương mại điện tử")
        c7 = Category(name="Logistics")
        db.session.add_all([c1, c2, c3, c4, c5, c6, c7])

        db.session.flush()

        # 3. Thêm Người dùng (User)
        password = str(hashlib.md5('123456'.encode('utf-8')).hexdigest())

        admin = User(name="Quản trị viên", username="admin", password=password,
                     user_role=UserRole.ADMIN, phone="0123456789", email="admin@gmail.com")

        # Công ty chuyên CNTT, Thiết kế và Ngôn ngữ
        emp1 = User(name='Tập đoàn Công nghệ & Sáng tạo ABC', username='employer1', password=password,
                    user_role=UserRole.EMPLOYER, phone="0988123456", email="employer1@gmail.com")

        # Công ty chuyên Marketing và Thương mại điện tử
        emp2 = User(name='Agency Truyền thông Media XYZ', username='employer2', password=password,
                    user_role=UserRole.EMPLOYER, phone="0977123456", email="employer2@gmail.com")

        # Công ty chuyên Logistics và Kế toán (Dịch vụ doanh nghiệp)
        emp3 = User(name='Tổng công ty Vận tải & Tài chính Toàn Cầu', username='employer3', password=password,
                    user_role=UserRole.EMPLOYER, phone="0966123456", email="employer3@gmail.com")

        cand1 = User(name='Ứng viên 1', username='candidate1', password=password,
                     user_role=UserRole.CANDIDATE, phone="0123456789", email="candidate1@gmail.com")

        #Tạo thêm candidate cand2
        cand2 = User(name='Ứng viên 2', username='candidate2', password=password,
                     user_role=UserRole.CANDIDATE, phone="0223456789", email="candidate2@gmail.com")
        db.session.add_all([admin, emp1, emp2, emp3, cand1, cand2])

        db.session.flush()

        # 4. Thêm Việc làm
        now = datetime.now()
        jobs_data = [
            # --- NHÓM CỦA EMP1 (CNTT, Thiết kế, Ngôn ngữ) ---
            Job(title='Lập trình viên Java (Senior)', description='Phát triển hệ thống Microservices.',
                salary=35000000, deadline=now + timedelta(days=30), category_id=c1.id, employer_id=emp1.id),
            Job(title='Chuyên viên Cyber Security', description='Bảo mật hệ thống Cloud.',
                salary=28000000, deadline=now + timedelta(days=25), category_id=c1.id, employer_id=emp1.id),
            Job(title='UI/UX Designer (Mobile App)', description='Thiết kế giao diện bằng Figma.',
                salary=20000000, deadline=now + timedelta(days=22), category_id=c5.id, employer_id=emp1.id),
            Job(title='Họa sĩ minh họa (Illustrator)', description='Vẽ nhân vật game 2D.',
                salary=17000000, deadline=now + timedelta(days=30), category_id=c5.id, employer_id=emp1.id),
            Job(title='Biên dịch viên phim', description='Dịch thuật và làm sub phim Mỹ.',
                salary=14000000, deadline=now - timedelta(days=18), category_id=c4.id, employer_id=emp1.id),

            # --- NHÓM CỦA EMP2 (Marketing, TMĐT) ---
            Job(title='Chuyên viên SEO/SEM', description='Tối ưu từ khóa Google Ads.',
                salary=15000000, deadline=now - timedelta(days=20), category_id=c2.id, employer_id=emp2.id),
            Job(title='Content Creator (TikTok)', description='Xây dựng kịch bản video xu hướng.',
                salary=12000000, deadline=now, category_id=c2.id, employer_id=emp2.id),
            Job(title='Brand Manager', description='Xây dựng chiến lược thương hiệu.',
                salary=40000000, deadline=now - timedelta(days=45), category_id=c2.id, employer_id=emp2.id),
            Job(title='Quản trị TikTok Shop', description='Vận hành gian hàng và livestream.',
                salary=13000000, deadline=now + timedelta(days=15), category_id=c6.id, employer_id=emp2.id),
            Job(title='Chuyên viên E-commerce', description='Quản lý gian hàng Shopee, Lazada.',
                salary=22000000, deadline=now + timedelta(days=40), category_id=c6.id, employer_id=emp2.id),

            # --- NHÓM CỦA EMP3 (Logistics, Kế toán, Ngôn ngữ) ---
            Job(title='Điều phối viên vận tải', description='Sắp xếp lịch trình xe tải Bắc Nam.',
                salary=11500000, deadline=now + timedelta(days=15), category_id=c7.id, employer_id=emp3.id),
            Job(title='Nhân viên Kế toán kho', description='Kiểm kê hàng hóa, chứng từ xuất nhập.',
                salary=9500000, deadline=now + timedelta(days=12), category_id=c3.id, employer_id=emp3.id),
            Job(title='Kế toán trưởng', description='Lập báo cáo tài chính cuối năm.',
                salary=25000000, deadline=now + timedelta(days=50), category_id=c3.id, employer_id=emp3.id),
            Job(title='Giảng viên tiếng Anh IELTS', description='Giảng dạy Speaking/Writing 8.0.',
                salary=30000000, deadline=now + timedelta(days=60), category_id=c4.id, employer_id=emp3.id),
            Job(title='Chuyên viên thu mua (Procurement)', description='Đàm phán với nhà cung cấp nước ngoài.',
                salary=18000000, deadline=now + timedelta(days=30), category_id=c7.id, employer_id=emp3.id)
        ]

        db.session.add_all(jobs_data)
        db.session.commit()