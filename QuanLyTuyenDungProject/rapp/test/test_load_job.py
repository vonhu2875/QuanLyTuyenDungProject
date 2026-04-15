from rapp.dao import load_jobs, normalize
from rapp.test.test_base import sample_job, test_app, test_session

#Unit test phân trang
def test_paging(test_app, sample_job):
    actual_jobs = load_jobs(page=1)
    assert len(actual_jobs) == test_app.config["PAGE_SIZE"]
    actual_jobs = load_jobs(page=3)
    assert len(actual_jobs) == 1

#Unit test tìm kiếm theo kw, page, cate_id

def test_kw(sample_job):
    actual_jobs = load_jobs(kw="lap trinh")
    assert len(actual_jobs) == 2
    assert all("lap trinh" in normalize(j.title) for j in actual_jobs)

def test_cate_id(sample_job):
    actual_jobs = load_jobs(cate_id=1)
    assert len(actual_jobs) == 1
    actual_jobs = load_jobs(cate_id=2)
    assert len(actual_jobs) == 1
    actual_jobs = load_jobs(cate_id=3)
    assert len(actual_jobs) == 3

def test_page_kw(sample_job):
    actual_jobs = load_jobs(page=1, kw="lap trinh")
    assert len(actual_jobs) == 2
    assert actual_jobs[0].title == 'Chuyên viên Lập trình C++'
    assert actual_jobs[1].title == 'Lập trình viên cấp cao'

def test_page_cate_id(sample_job):
    actual_jobs = load_jobs(page=1, cate_id=1)
    assert len(actual_jobs) == 1
    assert actual_jobs[0].title == 'Chuyên viên Phân tích Dữ liệu'
    actual_jobs = load_jobs(page=1, cate_id=3)
    assert len(actual_jobs) == 2
    assert actual_jobs[0].title == 'Kế toán viên - Trợ Lý'

def test_kw_cate_id(sample_job):
    actual_jobs = load_jobs(kw='ke toan', cate_id=1)
    assert len(actual_jobs) == 0
    actual_jobs = load_jobs(kw='ke toan', cate_id=3)
    assert len(actual_jobs) == 2
    assert all('ke toan' in normalize(j.title) and j.category_id == 3 for j in actual_jobs)

def test_kw_cate_id_page(sample_job):
    actual_jobs = load_jobs(kw='vien', cate_id=3, page=1)
    assert len(actual_jobs) == 2
    assert all('vien' in normalize(j.title) and j.category_id == 3 for j in actual_jobs)
    assert actual_jobs[0].title == 'Kế toán viên - Trợ Lý'
    actual_jobs = load_jobs(kw='vien', cate_id=3, page=2)
    assert len(actual_jobs) == 1
    assert all('vien' in normalize(j.title) and j.category_id == 3 for j in actual_jobs)
    assert actual_jobs[0].title == 'Lập trình viên cấp cao'

#Unit test invalid
def test_invalid_page_zero(sample_job):
    actual_jobs = load_jobs(page=0)
    assert len(actual_jobs) == 0
#Có phát hiện ra lỗi => vì code ban đầu là if page: Nên hiểu nhầm là false nên trả về luôn query.all()


def test_invalid_page_negative(sample_job):
    actual_jobs = load_jobs(page=-1)
    assert len(actual_jobs) == 0

def test_invalid_page_out_of_range(sample_job):
    actual_jobs = load_jobs(page=50)
    assert len(actual_jobs) == 0

def test_invalid_kw_empty(sample_job):
    actual_jobs = load_jobs(kw="")
    assert len(actual_jobs) == len(sample_job)

def test_invalid_kw_spaces(sample_job):
    actual_jobs = load_jobs(kw="   ")
    assert len(actual_jobs) == len(sample_job)
#Có fix lỗi bên trong hàm load_jobs ở chỗ if kw thêm and kw.strip()

def test_invalid_kw_not_found(sample_job):
    actual_jobs = load_jobs(kw="abcxyz")
    assert len(actual_jobs) == 0

def test_invalid_cate_id_not_exist(sample_job):
    actual_jobs = load_jobs(cate_id=20)
    assert len(actual_jobs) == 0

def test_invalid_cate_id_string(sample_job):
    actual_jobs = load_jobs(cate_id="abc")
    assert len(actual_jobs) == 0

def test_invalid_all(sample_job):
    actual_jobs = load_jobs(kw="abcxyz", cate_id=999, page=5)
    assert len(actual_jobs) == 0



