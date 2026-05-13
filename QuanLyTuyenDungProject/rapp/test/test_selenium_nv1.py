import os
import time

import pytest
from selenium import webdriver

from rapp.test.pages.LoginPage import LoginPage
from rapp.test.pages.JobCreatePage import JobCreatePage


@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

current_dir = os.path.dirname(os.path.abspath(__file__))


def test_create_job_success(driver):
    login = LoginPage(driver)
    job_create = JobCreatePage(driver)

    login.open_page()
    login.login('employer1', '123456')
    time.sleep(2)

    job_create.open_page()
    time.sleep(1)

    job_create.fill_form(
        title='Lập trình viên Python Senior',
        salary='20000000',
        deadline='2026-12-31',
        description='Yêu cầu kinh nghiệm thực chiến từ 2 năm trở lên.',
        category_index=1
    )
    job_create.submit()
    time.sleep(2)

    assert driver.current_url == 'http://127.0.0.1:5000/'
    driver.save_screenshot(os.path.join(current_dir, 'create_job_success.png'))


def test_create_job_title_too_short(driver):
    login = LoginPage(driver)
    job_create = JobCreatePage(driver)

    login.open_page()
    login.login('employer1', '123456')
    time.sleep(2)

    job_create.open_page()
    time.sleep(1)

    job_create.remove_title_minlength()
    job_create.fill_form(
        title='Ngắn',
        salary='10000000',
        deadline='2026-12-31',
        description='Mô tả hợp lệ.',
        category_index=1
    )
    job_create.submit()
    time.sleep(2)

    err = job_create.get_error_message()
    assert 'tiêu đề' in err.lower() or 'tối thiểu' in err.lower()
    driver.save_screenshot(os.path.join(current_dir, 'create_job_title_too_short.png'))


def test_create_job_invalid_salary(driver):
    login = LoginPage(driver)
    job_create = JobCreatePage(driver)

    login.open_page()
    login.login('employer1', '123456')
    time.sleep(2)

    job_create.open_page()
    time.sleep(1)

    job_create.fill_form(
        title='Nhân viên kinh doanh toàn thời gian',
        salary='0',
        deadline='2026-12-31',
        description='Mô tả hợp lệ.',
        category_index=1
    )
    job_create.submit()
    time.sleep(2)

    err = job_create.get_error_message()
    assert 'lương' in err.lower()
    driver.save_screenshot(os.path.join(current_dir, 'create_job_invalid_salary.png'))


def test_create_job_deadline_past(driver):
    login = LoginPage(driver)
    job_create = JobCreatePage(driver)

    login.open_page()
    login.login('employer1', '123456')
    time.sleep(2)

    job_create.open_page()
    time.sleep(1)

    job_create.fill_form(
        title='Kế toán tổng hợp kinh nghiệm 2 năm',
        salary='15000000',
        deadline='2020-01-01',
        description='Mô tả hợp lệ.',
        category_index=1
    )
    job_create.submit()
    time.sleep(2)

    err = job_create.get_error_message()
    assert 'deadline' in err.lower() or 'hạn' in err.lower()
    driver.save_screenshot(os.path.join(current_dir, 'create_job_deadline_past.png'))
