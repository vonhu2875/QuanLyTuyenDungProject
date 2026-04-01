import math

from flask import render_template, request
from rapp import dao, app, login


@app.route("/")
def index():
    cate_id = request.args.get('category_id')
    kw = request.args.get('kw')
    categories = dao.load_categories()
    page = int(request.args.get('page', 1))
    jobs = dao.load_jobs(cate_id, kw, page)
    return render_template("index.html", jobs=jobs, categories=categories,
                           pages=math.ceil(dao.count_jobs(cate_id) / app.config['PAGE_SIZE']))


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


if __name__ == "__main__":
    app.run(debug=True)
