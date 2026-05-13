from selenium.webdriver.common.by import By
from rapp.test.pages.BasePage import BasePage

class ManageJobPage(BasePage):
    BTN_TOGGLE = (By.CLASS_NAME, "btn-toggle")
    BTN_EDIT = (By.CSS_SELECTOR, "a.btn-outline-primary")
    BTN_DELETE = (By.CLASS_NAME, "btn-delete")

    def open_page(self):
        self.driver.get("http://127.0.0.1:5000/users/jobs")

    def click_toggle(self):
        self.driver.find_element(*self.BTN_TOGGLE).click()

    def click_edit(self):
        self.driver.find_element(*self.BTN_EDIT).click()

    def click_delete(self):
        self.driver.find_element(*self.BTN_DELETE).click()
        alert = self.driver.switch_to.alert
        alert.accept()