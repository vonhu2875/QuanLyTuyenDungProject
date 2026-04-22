from datetime import datetime, timedelta

import pytest
from cloudinary import uploader
from flask import Flask
from rapp import db
from rapp.models import Job

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['PAGE_SIZE'] = 2
    db.init_app(app)
    return app

@pytest.fixture
def test_app():
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def test_session(test_app):
    yield db.session
    db.session.rollback()

@pytest.fixture
def sample_job(test_session):
    # title = 'Chuyên viên Phân tích Dữ liệu',
    # description = 'Sử dụng SQL, Python để phân tích dữ liệu kinh doanh.',
    # salary = 20000000,
    # deadline = now + timedelta(days=20),
    # category_id = c1.id,
    # employer_id = emp2.id
    j1 = Job(title='Chuyên viên Phân tích Dữ liệu',description='Sử dụng SQL, Python để phân tích dữ liệu kinh doanh.',
             salary=20000,deadline= datetime.now() + timedelta(days=30),
             category_id=1,employer_id=1)

    j2 = Job(title='Chuyên viên Lập trình C++', description='Sử dụng C++.',
             salary=30000, deadline=datetime.now() + timedelta(days=50),
             category_id=2, employer_id=1)

    j3 = Job(title='Kế toán viên - Trợ Lý', description='Biết dùng excel.',
             salary=50000, deadline=datetime.now() + timedelta(days=10),
             category_id=3, employer_id=3)

    j4 = Job(title='Trưởng kế toán viên', description='Biết dùng excel.',
             salary=50000, deadline=datetime.now() + timedelta(days=10),
             category_id=3, employer_id=3)

    j5 = Job(title='Lập trình viên cấp cao', description='Biết dùng máy.',
             salary=50000, deadline=datetime.now() + timedelta(days=200),
             category_id=3, employer_id=1)

    test_session.add_all([j1, j2, j3, j4, j5])
    test_session.commit()
    return [j1, j2, j3, j4, j5]

@pytest.fixture
def mock_cloudinary(monkeypatch):
    def fake_upload(file):
        return {'secure_url': 'https://fake-avatar.png'}
    monkeypatch.setattr('cloudinary.uploader.upload', fake_upload)