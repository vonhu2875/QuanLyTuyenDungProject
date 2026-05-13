from rapp.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class JobCreatePage(BasePage):
    URL = 'http://127.0.0.1:5000/jobs/create'

    TITLE_INPUT = (By.ID, 'title')
    SALARY_INPUT = (By.ID, 'salary')
    DEADLINE_INPUT = (By.ID, 'deadline')
    CATEGORY_SELECT = (By.ID, 'category_id')
    DESCRIPTION_INPUT = (By.ID, 'description')
    SUBMIT_BUTTON = (By.CSS_SELECTOR, 'button[type=submit]')
    ERROR_ALERT = (By.CSS_SELECTOR, '.alert.alert-danger')

    def open_page(self):
        self.open(self.URL)

    def fill_form(self, title, salary, deadline, description, category_index=1):
        self.driver.execute_script("""
            document.getElementById('title').value = arguments[0];
            document.getElementById('salary').value = arguments[1];
            document.getElementById('deadline').value = arguments[2];
            document.getElementById('description').value = arguments[3];
        """, title, salary, deadline, description)
        select = Select(self.find(*self.CATEGORY_SELECT))
        select.select_by_index(category_index)

    def remove_title_minlength(self):
        self.driver.execute_script(
            "document.getElementById('title').removeAttribute('minlength')"
        )

    def submit(self):
        self.driver.execute_script("document.querySelector('form').submit()")

    def get_error_message(self):
        return self.read(*self.ERROR_ALERT)
