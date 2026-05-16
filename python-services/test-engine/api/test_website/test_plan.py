"""
计划模块测试用例
"""
import pytest
from common.assertions import assert_success, assert_true


class TestPlan:
    """计划 CRUD 测试"""

    @pytest.mark.p0
    def test_create_plan(self, client):
        """创建计划"""
        resp = client.post("/api/plan/add", data={
            "title": "API 测试计划",
            "description": "自动化测试创建的计划",
            "type": "功能",
            "environment": "DEV",
        })
        assert_success(resp, "创建计划应成功")

    @pytest.mark.p0
    def test_list_plans(self, client):
        """查询计划列表"""
        resp = client.get("/api/plan/list")
        assert_success(resp, "查询计划列表应成功")
        data = resp.get("data", {})
        records = data.get("records", data.get("list", []))
        assert isinstance(records, list), "计划列表应为数组"
