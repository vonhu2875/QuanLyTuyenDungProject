from rapp.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By

class ApplyJobPage(BasePage):
    URL = f'http://127.0.0.1:5000/jobs/{id}/applications'
    CV_INPUT = (By.ID, 'cv_file')
    CONFIRM_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    SUCCESS_ALERT = (By.CLASS_NAME, "alert-success")

    def open_page(self):
        self.open(self.URL)

    def upload_cv(self, file_path):
        self.typing(*self.CV_INPUT,file_path)

    def submit_application(self):
        self.click(*self.CONFIRM_BUTTON)

    def get_success_message(self):
        return self.read(*self.SUCCESS_ALERT)