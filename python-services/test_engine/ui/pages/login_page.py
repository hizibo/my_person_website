"""
登录页面 Page Object
"""
from .base_page import BasePage


class LoginPage(BasePage):
    def input_username(self, username: str):
        self.fill('input[name="username"]', username)

    def input_password(self, password: str):
        self.fill('input[name="password"]', password)

    def click_login(self):
        self.click('button[type="submit"]')

    def login(self, username: str, password: str):
        self.navigate("/login")
        self.input_username(username)
        self.input_password(password)
        self.click_login()

    def get_error_message(self) -> str:
        return self.get_text(".error-message") or self.get_text(".el-message--error")
