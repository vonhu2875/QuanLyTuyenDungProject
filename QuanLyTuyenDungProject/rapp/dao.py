from rapp.models import Category, Job, User
from flask import current_app


def get_user_by_id(user_id):
    return User.query.get(user_id)


def load_categories():
    return Category.query.all()

def load_jobs(cate_id=None, kw=None, page=None):
    query = Job.query
    if cate_id:
        query = query.filter(Job.category_id.__eq__(cate_id))

    if kw:
        query = query.filter(Job.title.contains(kw))
    if page:
        start = (page - 1) * current_app.config['PAGE_SIZE']
        query = query.slice(start, start + current_app.config['PAGE_SIZE'])
    return query.all()

def count_jobs(category_id=None):
    if category_id:
        return Job.query.filter(Job.category_id==category_id).count()
    return Job.query.count()
