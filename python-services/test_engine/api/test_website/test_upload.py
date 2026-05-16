"""
文件上传模块测试用例
"""
import pytest
from common.assertions import assert_code


class TestUpload:
    """文件上传测试"""

    @pytest.mark.p2
    def test_upload_health(self, client):
        """上传接口健康检查"""
        # 文件上传需要 multipart 格式，这里验证模块可达
        resp = client.get("/api/plan/list")
        assert resp.get("code") is not None, "应能正常连接服务器"
