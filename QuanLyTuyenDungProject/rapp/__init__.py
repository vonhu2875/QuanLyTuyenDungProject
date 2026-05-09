from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = '&(^&*^&*^U*HJBJKHJLHKJHK&*%^&5786985646858'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://123456@localhost/recruitmentdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 4
db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config(cloud_name='dphbawbuk',
api_key='985298798723894',
api_secret='zXvHaHmP9xO_UblF8hE6ZKfpUVk')