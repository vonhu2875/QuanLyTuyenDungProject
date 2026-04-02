import math

from flask import render_template, request, redirect
from flask_login import login_user, logout_user

from rapp import dao, app, login
from rapp.dao import add_user
from rapp.exceptions import ValidationError, DuplicateError
from rapp.models import User, UserRole


@app.route('/')
def index():
    cate_id = request.args.get('category_id')
    kw = request.args.get('kw')
    categories = dao.load_categories()
    page = int(request.args.get('page', 1))
    jobs = dao.load_jobs(cate_id, kw, page)
    return render_template("index.html", jobs=jobs, categories=categories,
                           pages=math.ceil(dao.count_jobs(cate_id) / app.config['PAGE_SIZE']))

@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/login', methods=['post'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)

    next = request.args.get('next')
    return redirect(next if next else '/')

@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')
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



@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == "__main__":
    app.run(debug=True)
