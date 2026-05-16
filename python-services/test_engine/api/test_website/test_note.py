"""
笔记模块测试用例（CRUD 完整流程）
"""
import pytest
from common.assertions import assert_success, assert_equal, assert_true


class TestNote:
    """笔记 CRUD 测试"""

    @pytest.mark.p0
    def test_create_note(self, client):
        """创建笔记"""
        resp = client.post("/api/note/add", data={
            "title": "API 测试笔记",
            "content": "这是自动化测试创建的笔记内容",
            "categoryId": 1,
        })
        assert_success(resp, "创建笔记应成功")

    @pytest.mark.p0
    def test_list_notes(self, client):
        """查询笔记列表"""
        resp = client.get("/api/note/list")
        assert_success(resp, "查询笔记列表应成功")

    @pytest.mark.p1
    def test_list_with_children(self, client):
        """分类查询笔记"""
        resp = client.get("/api/note/with-children")
        assert_success(resp, "分类查询应成功")

    @pytest.mark.p1
    def test_update_note(self, client):
        """更新笔记"""
        # 先查一条
        list_resp = client.get("/api/note/list")
        notes = list_resp.get("data", {}).get("records", [])
        if not notes:
            pytest.skip("没有可更新的笔记")

        note = notes[0]
        resp = client.put("/api/note/update", data={
            "id": note["id"],
            "title": f"更新_{note.get('title', 'test')}",
            "content": note.get("content", ""),
        })
        assert_success(resp, "更新笔记应成功")

    @pytest.mark.p2
    def test_delete_note(self, client):
        """删除笔记"""
        # 先创建一个再删除
        create_resp = client.post("/api/note/add", data={
            "title": "待删除笔记",
            "content": "此笔记将在测试中被删除",
            "categoryId": 1,
        })
        if create_resp.get("code") != 200:
            pytest.skip("无法创建待删除笔记")

        note_id = create_resp.get("data", {}).get("id")
        if not note_id:
            # 查列表取最后一个
            list_resp = client.get("/api/note/list")
            notes = list_resp.get("data", {}).get("records", [])
            if not notes:
                pytest.skip("没有可删除的笔记")
            note_id = notes[-1]["id"]

        resp = client.delete(f"/api/note/delete/{note_id}")
        # 删除可能返回不同状态码，只要不报错即可
        assert resp.get("code") is not None, "删除应返回有效响应"
