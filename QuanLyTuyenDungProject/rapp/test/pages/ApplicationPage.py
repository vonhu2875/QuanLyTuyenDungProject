import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from rapp.test.pages.BasePage import BasePage


class ApplicationPage(BasePage):
    BTN_OPEN_CANDIDATES = (By.CSS_SELECTOR, "button[data-bs-toggle='collapse']")

    SELECT_STATUS = (By.CLASS_NAME, "form-select")

    BTN_UPDATE = (By.CLASS_NAME, "btn-update-status")

    LINK_VIEW_CV = (By.PARTIAL_LINK_TEXT, "Xem CV")

    def open_page(self):
        self.driver.get("http://127.0.0.1:5000/applications")

    def expand_job_list(self):
        time.sleep(1)
        btn = self.driver.find_element(*self.BTN_OPEN_CANDIDATES)
        self.driver.execute_script("arguments[0].scrollIntoView();", btn)
        self.driver.execute_script("arguments[0].click();", btn)
        time.sleep(1.5)

    def update_first_candidate_status(self, status_value):
        dropdown = self.driver.find_element(*self.SELECT_STATUS)

        self.driver.execute_script("arguments[0].scrollIntoView();", dropdown)
        time.sleep(0.5)

        select = Select(dropdown)
        select.select_by_value(status_value)

        btn_update = self.driver.find_element(*self.BTN_UPDATE)
        self.driver.execute_script("arguments[0].click();", btn_update)