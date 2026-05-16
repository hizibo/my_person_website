"""
UI 测试共享 fixture
Playwright 浏览器管理、截图等
"""
import pytest
from config.settings import load_config


@pytest.fixture(scope="session")
def browser_config():
    cfg = load_config()
    return cfg.get("browser", {})


def pytest_bdd_apply_tag(tag, function):
    pass
