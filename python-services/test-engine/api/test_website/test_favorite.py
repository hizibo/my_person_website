"""
网站收藏模块测试用例
"""
import pytest
from common.assertions import assert_success, assert_code


class TestFavorite:
    """收藏功能测试"""

    @pytest.mark.p1
    def test_add_favorite(self, client):
        """添加收藏"""
        resp = client.post("/api/favorite/add", data={
            "url": "http://example.com",
            "title": "测试收藏网站",
            "icon": "http://example.com/favicon.ico",
        })
        assert_success(resp, "添加收藏应成功")

    @pytest.mark.p1
    def test_list_favorites(self, client):
        """查询收藏列表"""
        resp = client.get("/api/favorite/list")
        assert_success(resp, "查询收藏列表应成功")
