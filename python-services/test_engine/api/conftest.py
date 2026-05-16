"""
API 测试共享 fixture
提供 HTTP 客户端初始化、登录 Token 获取
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.http_client import HttpClient
from common.assertions import assert_success, assert_code
from config.settings import load_config


@pytest.fixture(scope="module")
def config():
    return load_config()


@pytest.fixture(scope="module")
def client(config):
    """创建已登录的 HTTP 客户端，模块级别复用"""
    website = config["website"]
    client = HttpClient(base_url=website["api_base"])

    # 登录获取 Token
    resp = client.post("/api/login", data={
        "username": website["admin_user"],
        "password": website["admin_password"],
    })

    # 提取 Token（兼容不同响应格式）
    token = None
    if resp.get("code") == 200:
        data = resp.get("data", {})
        token = data.get("token") or data.get("accessToken")
    elif resp.get("data", {}).get("token"):
        token = resp["data"]["token"]

    if token:
        client.set_token(token)
    else:
        pytest.skip(f"登录失败，无法获取 Token: {resp}")

    return client


@pytest.fixture(scope="module")
def unauth_client(config):
    """未登录的 HTTP 客户端"""
    website = config["website"]
    return HttpClient(base_url=website["api_base"])


@pytest.fixture(scope="module")
def base_url(config):
    return config["website"]["base_url"]
