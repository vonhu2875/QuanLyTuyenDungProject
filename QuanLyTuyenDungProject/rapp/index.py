import math
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from unicodedata import category

from rapp import dao, app, login, db
from rapp.dao import add_user, add_job
from rapp.exceptions import ValidationError, DuplicateError
from rapp.models import User, UserRole, Job, Category, Application

def register_routes_nv1(app):
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
            dao.add_user(name=data.get('name'), username=data.get('username'), password=password, avatar=request.files.get('avatar'),
                     email=data.get('email'), phone=data.get('phone'), user_role=UserRole[data.get('user_role')])
            return redirect('/login')
        except ValidationError as val:
            return render_template('register.html', err_msg=str(val), UserRole = users_show)
        except DuplicateError as dup:
            return render_template('register.html', err_msg=str(dup), UserRole = users_show)
        except Exception as ex:
            return render_template('register.html', err_msg=str(ex), UserRole = users_show)


    #Nghiệp vụ chính 1: Đăng tin tuyển dụng
    @app.route('/jobs/create')
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
            dao.add_job(title=title, description=description, salary=salary,deadline=deadline, category_id=category_id, employer_id=current_user.id,user_role = current_user.user_role)
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

#=========================Nghiệp vụ 2: Ngại và Hiền (Bé Hà)==========================

# JOB DETAILS
def register_routes_nv2(app):
    @app.route('/jobs/<int:job_id>')
    def job_detail(job_id):
        job = dao.get_job_by_id(job_id)

        applied = False

        if current_user.is_authenticated and current_user.user_role == UserRole.CANDIDATE:
            applied = dao.check_applied(current_user.id, job_id)

        return render_template('job_details.html', job=job, applied=applied, UserRole=UserRole)

    # Nghiệp vụ chính 2: Nộp hồ sơ
    @app.route('/jobs/<int:job_id>/applications', methods=['GET', 'POST'])
    @login_required
    def apply_job(job_id):
        job = dao.get_job_by_id(job_id)
        if not job:
            return "<h1>404 - Không tìm thấy công việc này!</h1>", 200

        if current_user.user_role != UserRole.CANDIDATE:
            return "<h1>403 - Lỗi quyền truy cập</h1><p>Chỉ Ứng viên mới được nộp hồ sơ!</p>", 200

        if request.method == 'POST':
            try:
                cv_file = request.files.get('cv_file')
                dao.apply_for_job(
                    job_id=job_id,
                    candidate_id=current_user.id,
                    user_role=current_user.user_role,
                    cv_file=cv_file
                )

                succ_msg = "Nộp hồ sơ thành công!"
                return render_template('apply_job.html', job=job, succ_msg=succ_msg)

            except (ValidationError, DuplicateError) as ex:
                return render_template('apply_job.html', job=job, err_msg=str(ex))

            except Exception as ex:
                err_msg = "Có lỗi xảy ra, vui lòng thử lại."
                return render_template('apply_job.html', job=job, err_msg=err_msg)

        return render_template('apply_job.html', job=job)

    # Liên hệ (Contact)
    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    #Hồ sơ cá nhân của CANDIDATE
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if request.method == 'POST':
            if dao.update_user_profile(current_user.id, request.form):
                succ_msg = "Cập nhật hồ sơ thành công!"
                return render_template('profile.html', succ_msg=succ_msg)
            else:
                err_msg = "Có lỗi xảy ra khi cập nhật."
                return render_template('profile.html', err_msg=err_msg)

        return render_template('profile.html')

    # Việc làm đã nộp
    @app.route('/profile/applications')
    @login_required
    def my_applications():
        if current_user.user_role != UserRole.CANDIDATE:
            return redirect(url_for('index'))

        applications = dao.get_my_applications(current_user.id)
        return render_template('my_applications.html', applications=applications, UserRole=UserRole)

#=========================Nghiệp vụ 3: Đẹp trai có gì sai (Nhu Toàn )==========================

def register_routes_nv3(app):
    @app.route('/applications')
    @login_required
    def all_applications():
        if current_user.user_role == UserRole.CANDIDATE:
            return redirect('/')
        apps_by_job = dao.get_apps_by_employer(current_user.id, current_user.user_role)
        return render_template('manage_applications.html', apps_by_job=apps_by_job, now=datetime.now())

    # Cập nhật trạng thái hồ sơ (EMPLOYER/ADMIN)
    @app.route('/applications/<int:app_id>/status', methods=['PATCH'])
    @login_required
    def update_status(app_id):
        if current_user.user_role == UserRole.CANDIDATE:
            return jsonify(success=False, message="Bạn không có quyền thực hiện thao tác này."), 403

        application = dao.get_application_by_id(app_id)
        if not application:
            return jsonify(success=False, message="Hồ sơ không tồn tại."), 404

        new_status = request.form.get('status')
        try:
            dao.update_application_status(
                app_id=app_id,
                new_status=new_status,
                updater_id=current_user.id,
                updater_role=current_user.user_role
            )
            flash("Cập nhật trạng thái thành công!", "success")
            return redirect(url_for('all_applications'))
        except (ValidationError, DuplicateError) as ex:
            flash(str(ex), "danger")
            return redirect(url_for('all_applications'))
        except Exception as ex:
            flash(str(ex), "danger")
            return redirect(url_for('all_applications'))


    # Quản lý tin đăng
    @app.route('/users/jobs')
    @login_required
    def manage_jobs():
        if current_user.user_role.name not in ['EMPLOYER', 'ADMIN']:
            return redirect('/')

        if current_user.user_role == UserRole.ADMIN:
            user_jobs = Job.query.all()
        else:
            user_jobs = current_user.jobs

        return render_template('manage_jobs.html',
                               jobs=user_jobs,
                               now=datetime.now())

    @app.route('/jobs/<int:job_id>/edit', methods=['GET'])
    @app.route('/jobs/<int:job_id>', methods=['PATCH', 'DELETE'])
    @login_required
    def manage_job(job_id):
        job = Job.query.get_or_404(job_id)

        if request.method == 'GET':
            categories = dao.get_categories()
            return render_template('edit_job.html', job=job, categories=categories)

        if request.method == 'DELETE':
            if current_user.user_role == UserRole.ADMIN or job.employer_id == current_user.id:
                Application.query.filter_by(job_id=job_id).delete()
                db.session.delete(job)
                db.session.commit()
            return jsonify(success=True)

        # PATCH
        if request.form.get('action') == 'toggle':
            if current_user.user_role == UserRole.EMPLOYER and job.employer_id != current_user.id:
                return jsonify(success=False, message="Bạn không có quyền thực hiện thao tác này!"), 403
            dao.toggle_job_active(job_id)
            return jsonify(success=True)

        try:
            if dao.update_job(job_id, request.form):
                return jsonify(success=True, redirect=url_for('manage_jobs'))
        except ValidationError as val:
            return jsonify(success=False, error=str(val))
        except Exception as ex:
            return jsonify(success=False, error=str(ex))


#========================================================================


if __name__ == "__main__":
    register_routes_nv1(app)
    register_routes_nv2(app)
    register_routes_nv3(app)
    app.run(debug=True)
