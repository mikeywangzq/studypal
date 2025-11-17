"""
Test Cache Service
"""
import pytest
import time
from app.services.cache_service import CacheService


class TestCacheService:
    """测试缓存服务"""

    @pytest.fixture
    def cache_service(self):
        """创建缓存服务实例"""
        service = CacheService()
        # 清除所有缓存确保测试环境干净
        service.clear_all()
        return service

    def test_cache_service_initialization(self, cache_service):
        """测试缓存服务初始化"""
        assert cache_service is not None
        assert cache_service.rag_cache is not None
        assert cache_service.vector_search_cache is not None
        assert cache_service.classification_cache is not None

    def test_rag_cache_set_and_get(self, cache_service):
        """测试 RAG 缓存的设置和获取"""
        question = "什么是操作系统？"
        result = {
            "answer": "操作系统是管理计算机硬件和软件资源的程序。",
            "sources": []
        }

        # 设置缓存
        cache_service.set_rag_result(question, result)

        # 获取缓存
        cached_result = cache_service.get_rag_result(question)

        assert cached_result is not None
        assert cached_result["answer"] == result["answer"]

    def test_rag_cache_with_conversation_id(self, cache_service):
        """测试带会话ID的 RAG 缓存"""
        question = "什么是操作系统？"
        conversation_id = "conv-123"
        result = {"answer": "测试答案"}

        # 设置缓存
        cache_service.set_rag_result(question, result, conversation_id)

        # 使用相同会话ID获取
        cached_result = cache_service.get_rag_result(question, conversation_id)
        assert cached_result is not None

        # 使用不同会话ID获取（应该返回None）
        cached_result_diff = cache_service.get_rag_result(question, "conv-456")
        assert cached_result_diff is None

    def test_rag_cache_miss(self, cache_service):
        """测试 RAG 缓存未命中"""
        # 获取不存在的缓存
        result = cache_service.get_rag_result("不存在的问题xyz123")
        assert result is None

    def test_vector_search_cache(self, cache_service):
        """测试向量搜索缓存"""
        query = "页表机制"
        k = 5
        search_results = [("doc1", 0.9), ("doc2", 0.8)]

        # 设置缓存
        cache_service.set_vector_search_result(query, search_results, k)

        # 获取缓存
        cached_results = cache_service.get_vector_search_result(query, k)

        assert cached_results is not None
        assert len(cached_results) == len(search_results)

    def test_vector_search_cache_different_k(self, cache_service):
        """测试不同k值的向量搜索缓存"""
        query = "页表机制"
        results_k5 = [("doc1", 0.9), ("doc2", 0.8)]
        results_k10 = [("doc1", 0.9), ("doc2", 0.8), ("doc3", 0.7)]

        # 设置不同k值的缓存
        cache_service.set_vector_search_result(query, results_k5, k=5)
        cache_service.set_vector_search_result(query, results_k10, k=10)

        # 获取k=5的缓存
        cached_k5 = cache_service.get_vector_search_result(query, k=5)
        assert cached_k5 is not None
        assert len(cached_k5) == 2

        # 获取k=10的缓存
        cached_k10 = cache_service.get_vector_search_result(query, k=10)
        assert cached_k10 is not None
        assert len(cached_k10) == 3

    def test_classification_cache(self, cache_service):
        """测试分类缓存"""
        title = "test_note.md"
        content_hash = "abc123def456"
        classification_result = {
            "category": "操作系统",
            "tags": ["进程", "内存"],
            "confidence": 0.95
        }

        # 设置缓存
        cache_service.set_classification_result(
            title, content_hash, classification_result
        )

        # 获取缓存
        cached_result = cache_service.get_classification_result(
            title, content_hash
        )

        assert cached_result is not None
        assert cached_result["category"] == "操作系统"
        assert len(cached_result["tags"]) == 2

    def test_classification_cache_different_content(self, cache_service):
        """测试不同内容的分类缓存"""
        title = "test_note.md"
        hash1 = "hash1"
        hash2 = "hash2"
        result1 = {"category": "操作系统"}
        result2 = {"category": "数据库"}

        # 设置两个缓存
        cache_service.set_classification_result(title, hash1, result1)
        cache_service.set_classification_result(title, hash2, result2)

        # 分别获取
        cached1 = cache_service.get_classification_result(title, hash1)
        cached2 = cache_service.get_classification_result(title, hash2)

        assert cached1["category"] == "操作系统"
        assert cached2["category"] == "数据库"

    def test_cache_invalidation(self, cache_service):
        """测试缓存失效"""
        # 设置一些缓存
        cache_service.set_rag_result("q1", {"answer": "a1"})
        cache_service.set_vector_search_result("q2", [])

        # 清除所有缓存
        cache_service.clear_all()

        # 验证缓存已清空
        assert cache_service.get_rag_result("q1") is None
        assert cache_service.get_vector_search_result("q2") is None

    def test_vector_search_cache_invalidation(self, cache_service):
        """测试向量搜索缓存失效"""
        # 设置缓存
        cache_service.set_vector_search_result("test", [])

        # 失效缓存
        cache_service.invalidate_vector_search_cache()

        # 验证缓存已清空
        assert cache_service.get_vector_search_result("test") is None

    def test_get_cache_stats(self, cache_service):
        """测试获取缓存统计信息"""
        stats = cache_service.get_cache_stats()

        assert isinstance(stats, dict)
        assert "enabled" in stats
        assert "rag_cache" in stats
        assert "vector_search_cache" in stats
        assert "classification_cache" in stats

        # 验证每个缓存的统计信息
        assert "size" in stats["rag_cache"]
        assert "maxsize" in stats["rag_cache"]
        assert "size" in stats["vector_search_cache"]
        assert "maxsize" in stats["vector_search_cache"]

    def test_cache_size_limits(self, cache_service):
        """测试缓存大小限制"""
        stats = cache_service.get_cache_stats()

        # 验证缓存有大小限制
        assert stats["rag_cache"]["maxsize"] > 0
        assert stats["vector_search_cache"]["maxsize"] > 0
        assert stats["classification_cache"]["maxsize"] > 0

    def test_cache_lru_eviction(self, cache_service):
        """测试 LRU 缓存淘汰策略"""
        # 向量搜索缓存使用 LRU 策略
        max_size = cache_service.vector_search_cache.maxsize

        # 填满缓存
        for i in range(max_size + 10):
            cache_service.set_vector_search_result(
                query=f"query_{i}",
                result=[],
                k=5
            )

        # 验证缓存大小不超过限制
        stats = cache_service.get_cache_stats()
        assert stats["vector_search_cache"]["size"] <= max_size

    def test_cache_disabled(self):
        """测试禁用缓存的情况"""
        # 创建一个禁用缓存的服务
        service = CacheService()
        service.enabled = False

        question = "test"
        result = {"answer": "test"}

        # 设置缓存（应该不会真正缓存）
        service.set_rag_result(question, result)

        # 尝试获取（应该返回None）
        cached = service.get_rag_result(question)
        assert cached is None
