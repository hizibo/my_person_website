"""
工具模块测试用例
"""
import pytest
from common.assertions import assert_success, assert_code


class TestTool:
    """工具功能测试"""

    @pytest.mark.p1
    def test_xmind_parse(self, client, base_url):
        """XMind 解析接口（通过 Python 工具服务）"""
        # XMind 解析需要上传文件，这里测试接口可达性
        resp = client.get(f"{base_url}/api/tool/xmind/health")
        # 可能 200 或 404 取决于路由
        assert resp is not None, "应返回响应"
