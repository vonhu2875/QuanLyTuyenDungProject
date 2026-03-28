from rapp.models import Category, Job, User


def get_user_by_id(user_id):
    return User.query.get(user_id)


def load_categories():
    return Category.query.all()

def load_jobs(cate_id=None, kw=None):
    query = Job.query
    if cate_id:
        query = query.filter(Job.category_id.__eq__(cate_id))

    if kw:
        query = query.filter(Job.title.contains(kw))

    return query.all()
