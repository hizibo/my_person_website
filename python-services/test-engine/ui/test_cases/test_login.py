"""
UI 登录测试（示例）
需要先安装 Playwright 浏览器：playwright install chromium
"""
import pytest


@pytest.mark.skip(reason="需要浏览器环境，本地调试时取消 skip")
class TestLoginUI:
    def test_login_success(self, page):
        from ui.pages.login_page import LoginPage

        login_page = LoginPage(page, base_url="http://175.178.98.241")
        login_page.login("admin", "<password>")
        assert login_page.is_visible(".tool-header") or login_page.is_visible(".main-content")

    def test_login_failure(self, page):
        from ui.pages.login_page import LoginPage

        login_page = LoginPage(page, base_url="http://175.178.98.241")
        login_page.login("admin", "wrong_password")
        assert login_page.get_error_message() or not login_page.is_visible(".main-content")
