import math
from datetime import datetime

from flask import render_template, request, redirect
from flask_login import login_user, logout_user, login_required, current_user
from unicodedata import category

from rapp import dao, app, login
from rapp.dao import add_user, add_job
from rapp.exceptions import ValidationError, DuplicateError
from rapp.models import User, UserRole

#TRANG CHỦ
@app.route('/')
def index():
    cate_id = request.args.get('category_id')
    kw = request.args.get('kw')
    categories = dao.load_categories()
    page = int(request.args.get('page', 1))
    jobs = dao.load_jobs(cate_id, kw, page)
    return render_template("index.html", jobs=jobs, categories=categories,
                           pages=math.ceil(dao.count_jobs(cate_id) / app.config['PAGE_SIZE']))

#LOGIN
@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/login', methods=['post'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
        next = request.args.get('next')
        return redirect(next if next else '/')
    except ValidationError as val:
        return render_template('login.html', err_msg=str(val))
    except DuplicateError as dup:
        return render_template('login.html', err_msg=str(dup))
    except Exception as ex:
        return render_template('login.html', err_msg=str(ex))
#LOGOUT
@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')

#REGISTER
@app.route('/register')
def register_view():
    users_show = [UserRole.EMPLOYER, UserRole.CANDIDATE]
    return render_template('register.html', UserRole = users_show)

@app.route('/register', methods=['post'])
def register_process():
    users_show = [UserRole.EMPLOYER, UserRole.CANDIDATE]
    data = request.form

    password = data.get("password")
    confirm = data.get("confirm")
    if password != confirm:
        err_msg = "Mật khẩu không khớp!"
        return render_template('register.html', err_msg=err_msg,UserRole = users_show)
    try:
        add_user(name=data.get('name'), username=data.get('username'), password=password, avatar=request.files.get('avatar'),
                 email=data.get('email'), phone=data.get('phone'), user_role=data.get('user_role'))
        return redirect('/login')
    except ValidationError as val:
        return render_template('register.html', err_msg=str(val), UserRole = users_show)
    except DuplicateError as dup:
        return render_template('register.html', err_msg=str(dup), UserRole = users_show)
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex), UserRole = users_show)


#Nghiệp vụ chính 1: Đăng tin tuyển dụng
@app.route('/jobs')
@login_required
def job_view():
    if current_user.user_role not in [UserRole.EMPLOYER, UserRole.ADMIN]:
        return redirect('/login')
    categories = dao.load_categories()
    return render_template('job.html', categories=categories)

@app.route('/jobs', methods=['POST'])
@login_required
def create_job():
    categories = dao.load_categories()
    data = request.form
    title = data.get('title')
    description = data.get('description')
    salary = (data.get('salary'))
    deadline_str = data.get('deadline')
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    category_id = int(data.get('category_id'))
    try:
        add_job(title=title, description=description, salary=salary,deadline=deadline, category_id=category_id, employer_id=current_user.id,user_role = current_user.user_role)
        return redirect('/')
    except ValidationError as val:
        return render_template('job.html', err_msg=str(val), categories=categories)
    except DuplicateError as dup:
        return render_template('job.html', err_msg=str(dup), categories=categories)
    except Exception as ex:
        return render_template('job.html', err_msg=str(ex), categories=categories)


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

if __name__ == "__main__":
    app.run(debug=True)
