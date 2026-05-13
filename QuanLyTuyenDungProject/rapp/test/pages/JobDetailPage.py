from rapp.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

class JobDetailPage(BasePage):
    APPLY_BUTTON = (By.CSS_SELECTOR, '.job-detail-container .btn')

    def open_page(self, job_id):
        url = f'http://127.0.0.1:5000/jobs/{job_id}'
        self.open(url)

    def click_apply(self):
        self.click(*self.APPLY_BUTTON)