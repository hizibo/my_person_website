"""
Playwright Page Object 基类
封装常用浏览器操作，子页面继承后使用
"""
from playwright.sync_api import Page, Locator, expect
from typing import Optional
from pathlib import Path


class BasePage:
    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")
        self.page.wait_for_load_state("networkidle")

    def find(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, selector: str):
        self.page.locator(selector).click()

    def fill(self, selector: str, text: str):
        self.page.locator(selector).fill(text)

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).text_content() or ""

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def wait_for(self, selector: str, timeout: int = 10000):
        self.page.wait_for_selector(selector, timeout=timeout)

    def screenshot(self, name: str = "screenshot"):
        path = Path("reports/screenshots")
        path.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=f"{path}/{name}.png")
