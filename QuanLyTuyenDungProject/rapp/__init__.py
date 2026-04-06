from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = '&(^&*^&*^U*HJBJKHJLHKJHK&*%^&5786985646858'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Nhu...10c11c12cDHc@localhost/recruitmentdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config(cloud_name='dqrfckaek',
api_key='437884531811869',
api_secret='Bd3xRrxodvxmSl4QrgcVqUedoZE')