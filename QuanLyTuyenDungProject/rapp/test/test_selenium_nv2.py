import time
import os
from rapp.test.pages.LoginPage import LoginPage
from rapp.test.pages.JobDetailPage import JobDetailPage
from rapp.test.pages.ApplyJobPage import ApplyJobPage
from rapp.test.test_base import driver
from selenium.webdriver.common.by import By

current_dir = os.path.dirname(os.path.abspath(__file__))
def test_login_from_detail_list_job(driver):
    login = LoginPage(driver)
    login.open_page(url='http://127.0.0.1:5000/login?next=/jobs/1')
    login.login('candidate1', '123456')
    time.sleep(2)
    assert driver.current_url == 'http://127.0.0.1:5000/jobs/1'
    e = driver.find_element(By.CSS_SELECTOR, '#navbarNav > div > div > button > span')
    assert 'Ứng viên 1' in e.text
    driver.save_screenshot(os.path.join(current_dir, "login_from_list_job_success.png"))

def test_apply_job_success(driver):
    login_page = LoginPage(driver=driver)
    job_detail_page = JobDetailPage(driver=driver)
    apply_page = ApplyJobPage(driver=driver)

    login_page.open_page()
    login_page.login('candidate1', '123456')
    time.sleep(2)

    job_detail_page.open_page(job_id=1)
    time.sleep(2)

    job_detail_page.click_apply()
    time.sleep(2)
    cv_path = os.path.abspath(os.path.join(current_dir, "..", "..", "FileTestCase", "MB0_2.pdf"))

    driver.execute_script('window.scrollTo(0, 200)')
    time.sleep(2)
    apply_page.upload_cv(cv_path)
    apply_page.submit_application()
    time.sleep(2)
    success_msg = apply_page.get_success_message()
    assert "thành công" in success_msg.lower()
    driver.save_screenshot(os.path.join(current_dir, "apply_job_success.png"))