"""
登录认证模块测试用例
"""
import pytest
from common.assertions import assert_code, assert_equal, assert_true, assert_success


class TestLogin:
    """登录认证测试"""

    @pytest.mark.p0
    def test_admin_login_success(self, client):
        """管理员正确登录"""
        resp = client.get("/api/plan/list")
        assert_success(resp, "登录后应能正常访问受保护接口")

    @pytest.mark.p1
    def test_login_wrong_password(self, unauth_client):
        """密码错误登录"""
        resp = unauth_client.post("/api/login", data={
            "username": "admin",
            "password": "wrong_password_123",
        })
        # 期望返回非 200
        assert resp.get("code") != 200, "密码错误应返回非 200"

    @pytest.mark.p0
    def test_unauthorized_access(self, unauth_client):
        """未登录访问需认证接口"""
        resp = unauth_client.get("/api/note/list")
        # 期望 401 或被拦截
        code = resp.get("code")
        assert code is not None and code != 200, f"未登录应被拦截，实际 code={code}"
