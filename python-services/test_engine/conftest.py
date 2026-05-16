"""
全局 pytest 配置
提供全局 fixture、hook 等
"""
import pytest
import os
import sys

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def pytest_configure(config):
    config.addinivalue_line("markers", "allure_label: Allure 标签")


@pytest.fixture(scope="session")
def project_root():
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(scope="session")
def config():
    from config.settings import load_config
    return load_config()
