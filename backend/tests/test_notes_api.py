"""
Test Notes API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import uuid


class TestNotesAPI:
    """测试笔记 API"""

    def test_health_check(self, client: TestClient):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_get_available_categories(self, client: TestClient):
        """测试获取可用分类列表"""
        response = client.get("/api/notes/categories/available")
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "操作系统" in categories
        assert "数据库" in categories

    def test_get_notes_empty(self, client: TestClient):
        """测试获取笔记列表（空列表）"""
        response = client.get("/api/notes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["notes"] == []
        assert data["page"] == 1

    def test_get_notes_with_filters(self, client: TestClient):
        """测试带过滤条件获取笔记"""
        # 测试分类过滤
        response = client.get("/api/notes?category=操作系统")
        assert response.status_code == 200

        # 测试标签过滤
        response = client.get("/api/notes?tags=xv6,RISC-V")
        assert response.status_code == 200

        # 测试分页
        response = client.get("/api/notes?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10

    def test_get_note_not_found(self, client: TestClient):
        """测试获取不存在的笔记"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/notes/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_note_not_found(self, client: TestClient):
        """测试更新不存在的笔记"""
        fake_id = str(uuid.uuid4())
        update_data = {
            "title": "更新的标题",
            "category": "数据库"
        }
        response = client.put(f"/api/notes/{fake_id}", json=update_data)
        assert response.status_code == 404

    def test_delete_note_not_found(self, client: TestClient):
        """测试删除不存在的笔记"""
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/notes/{fake_id}")
        assert response.status_code == 404

    def test_search_notes_invalid_query(self, client: TestClient):
        """测试无效的搜索查询"""
        # 空查询字符串
        response = client.get("/api/notes/search/?query=")
        assert response.status_code == 422  # Validation error


class TestNoteUpload:
    """测试笔记上传功能"""

    def test_upload_without_files(self, client: TestClient):
        """测试不带文件的上传请求"""
        response = client.post("/api/notes/upload")
        assert response.status_code == 422  # Validation error

    def test_upload_with_auto_classify(self, client: TestClient):
        """测试带自动分类的上传"""
        # 这个测试需要有效的 OpenAI API key
        # 在实际环境中会跳过或使用 mock
        pass

    def test_upload_file_size_limit(self, client: TestClient):
        """测试文件大小限制"""
        # 创建一个超大文件并测试
        pass


class TestNoteSearch:
    """测试笔记搜索功能"""

    def test_search_notes_empty_result(self, client: TestClient):
        """测试搜索无结果"""
        response = client.get("/api/notes/search/?query=不存在的内容xyz123")
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        # 可能为空列表

    def test_search_notes_with_limit(self, client: TestClient):
        """测试带结果数量限制的搜索"""
        response = client.get("/api/notes/search/?query=操作系统&k=3")
        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)
        assert len(results) <= 3

    def test_search_invalid_limit(self, client: TestClient):
        """测试无效的结果数量限制"""
        # 超出范围的 k 值
        response = client.get("/api/notes/search/?query=test&k=100")
        assert response.status_code == 422  # Should validate k <= 20
