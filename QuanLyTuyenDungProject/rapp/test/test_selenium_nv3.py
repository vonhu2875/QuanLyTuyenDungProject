import time
import os
import pytest
from selenium.webdriver.common.by import By
from rapp.test.pages.LoginPage import LoginPage
from rapp.test.pages.ManageJobPage import ManageJobPage
from rapp.test.pages.ApplicationPage import ApplicationPage
from rapp.test.test_base import driver

current_dir = os.path.dirname(os.path.abspath(__file__))


# 1. Test quản lý hồ sơ
def test_manage_applications(driver):
    login = LoginPage(driver)
    manage_app = ApplicationPage(driver)

    login.open_page()
    login.login('employer1', '123456')
    time.sleep(2)

    manage_app.open_page()
    time.sleep(1)

    manage_app.expand_job_list()
    time.sleep(1)

    manage_app.update_first_candidate_status('INTERVIEW')
    time.sleep(2)

    assert "Quản lý hồ sơ ứng tuyển" in driver.page_source
    driver.save_screenshot(os.path.join(current_dir, "nv3_1_manage_apps.png"))


# 2. Test bảo mật
def test_security(driver):
    login = LoginPage(driver)

    driver.get("http://127.0.0.1:5000/logout")
    time.sleep(1)

    # Candidate cố vào trang của Employer
    login.login('candidate1', '123456')
    time.sleep(2)
    driver.get("http://127.0.0.1:5000/users/jobs")
    time.sleep(2)
    assert driver.current_url == "http://127.0.0.1:5000/"

    # Employer cố nộp hồ sơ
    driver.get("http://127.0.0.1:5000/logout")
    login.login('employer1', '123456')
    time.sleep(1)
    driver.get("http://127.0.0.1:5000/jobs/1/applications")
    time.sleep(1)
    assert "403" in driver.page_source or "Lỗi quyền truy cập" in driver.page_source

    driver.save_screenshot(os.path.join(current_dir, "nv3_2_security.png"))