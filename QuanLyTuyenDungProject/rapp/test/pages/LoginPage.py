from rapp.test.pages.BasePage import BasePage
from selenium.webdriver.common.by import By


class LoginPage(BasePage):
    URL = 'http://127.0.0.1:5000/login'

    USERNAME = (By.ID, 'username')
    PASSWORD = (By.ID, 'password')
    LOGIN_BUTTON =(By.CSS_SELECTOR, '.container form button[type=submit]')

    def open_page(self, url=URL):
        self.open(url)

    def login(self, username, password):
        self.typing(*self.USERNAME, username)
        self.typing(*self.PASSWORD, password)
        self.click(*self.LOGIN_BUTTON)

