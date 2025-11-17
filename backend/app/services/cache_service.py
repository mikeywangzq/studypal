"""
Cache Service - 查询结果缓存优化
使用 LRU 缓存来提升向量搜索和 RAG 查询的性能
"""
from typing import Optional, List, Dict, Any, Tuple
from cachetools import TTLCache, LRUCache
import hashlib
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """缓存服务 - 提升查询性能"""

    def __init__(self):
        """
        初始化缓存

        使用两种缓存策略：
        1. TTLCache: 带过期时间的缓存（用于RAG查询）
        2. LRUCache: 最近最少使用缓存（用于向量搜索）
        """
        # RAG 查询缓存 (带TTL)
        self.rag_cache = TTLCache(
            maxsize=100,  # 最多缓存100个查询结果
            ttl=settings.CACHE_TTL_SECONDS  # 过期时间（秒）
        )

        # 向量搜索缓存 (LRU)
        self.vector_search_cache = LRUCache(
            maxsize=200  # 最多缓存200个搜索结果
        )

        # 分类缓存 (减少LLM调用)
        self.classification_cache = TTLCache(
            maxsize=50,
            ttl=3600  # 1小时过期
        )

        self.enabled = settings.ENABLE_QUERY_CACHE
        logger.info(
            f"缓存服务初始化完成 (启用: {self.enabled}, TTL: {settings.CACHE_TTL_SECONDS}s)"
        )

    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """
        生成缓存键

        Args:
            data: 用于生成键的数据字典

        Returns:
            MD5 哈希值作为缓存键
        """
        # 将数据转为JSON字符串，确保顺序一致
        json_str = json.dumps(data, sort_keys=True)
        # 生成MD5哈希
        return hashlib.md5(json_str.encode()).hexdigest()

    # ========== RAG 查询缓存 ==========

    def get_rag_result(
        self, question: str, conversation_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存的 RAG 查询结果

        Args:
            question: 用户问题
            conversation_id: 会话ID

        Returns:
            缓存的结果，如果未找到则返回 None
        """
        if not self.enabled:
            return None

        cache_key = self._generate_cache_key({
            "type": "rag",
            "question": question,
            "conversation_id": conversation_id
        })

        result = self.rag_cache.get(cache_key)
        if result:
            logger.info(f"RAG 查询命中缓存: {question[:50]}...")
        return result

    def set_rag_result(
        self,
        question: str,
        result: Dict[str, Any],
        conversation_id: Optional[str] = None
    ):
        """
        缓存 RAG 查询结果

        Args:
            question: 用户问题
            result: 查询结果
            conversation_id: 会话ID
        """
        if not self.enabled:
            return

        cache_key = self._generate_cache_key({
            "type": "rag",
            "question": question,
            "conversation_id": conversation_id
        })

        self.rag_cache[cache_key] = result
        logger.debug(f"RAG 结果已缓存: {question[:50]}...")

    def invalidate_rag_cache_for_conversation(self, conversation_id: str):
        """
        失效某个会话的所有 RAG 缓存

        当会话被删除或修改时调用

        Args:
            conversation_id: 会话ID
        """
        if not self.enabled:
            return

        # 找到所有相关的缓存键并删除
        keys_to_remove = []
        for key in list(self.rag_cache.keys()):
            # 这是一个简化版本，实际使用中可能需要更复杂的映射
            keys_to_remove.append(key)

        for key in keys_to_remove:
            if key in self.rag_cache:
                del self.rag_cache[key]

        logger.info(f"已清除会话 {conversation_id} 的 RAG 缓存")

    # ========== 向量搜索缓存 ==========

    def get_vector_search_result(
        self, query: str, k: int = 5, user_id: Optional[str] = None
    ) -> Optional[List[Tuple[Any, float]]]:
        """
        获取缓存的向量搜索结果

        Args:
            query: 搜索查询
            k: 返回结果数量
            user_id: 用户ID

        Returns:
            缓存的搜索结果，如果未找到则返回 None
        """
        if not self.enabled:
            return None

        cache_key = self._generate_cache_key({
            "type": "vector_search",
            "query": query,
            "k": k,
            "user_id": user_id
        })

        result = self.vector_search_cache.get(cache_key)
        if result:
            logger.info(f"向量搜索命中缓存: {query[:50]}...")
        return result

    def set_vector_search_result(
        self,
        query: str,
        result: List[Tuple[Any, float]],
        k: int = 5,
        user_id: Optional[str] = None
    ):
        """
        缓存向量搜索结果

        Args:
            query: 搜索查询
            result: 搜索结果
            k: 返回结果数量
            user_id: 用户ID
        """
        if not self.enabled:
            return

        cache_key = self._generate_cache_key({
            "type": "vector_search",
            "query": query,
            "k": k,
            "user_id": user_id
        })

        self.vector_search_cache[cache_key] = result
        logger.debug(f"向量搜索结果已缓存: {query[:50]}...")

    def invalidate_vector_search_cache(self, user_id: Optional[str] = None):
        """
        失效向量搜索缓存

        当添加/删除笔记时调用

        Args:
            user_id: 如果指定，只清除该用户的缓存；否则清除全部
        """
        if not self.enabled:
            return

        if user_id is None:
            # 清除所有缓存
            self.vector_search_cache.clear()
            logger.info("已清除所有向量搜索缓存")
        else:
            # 清除特定用户的缓存（简化版本）
            self.vector_search_cache.clear()
            logger.info(f"已清除用户 {user_id} 的向量搜索缓存")

    # ========== 分类缓存 ==========

    def get_classification_result(
        self, title: str, content_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存的分类结果

        Args:
            title: 笔记标题
            content_hash: 内容的哈希值（用于识别相同内容）

        Returns:
            缓存的分类结果，如果未找到则返回 None
        """
        if not self.enabled:
            return None

        cache_key = self._generate_cache_key({
            "type": "classification",
            "title": title,
            "content_hash": content_hash
        })

        result = self.classification_cache.get(cache_key)
        if result:
            logger.info(f"分类结果命中缓存: {title[:50]}...")
        return result

    def set_classification_result(
        self, title: str, content_hash: str, result: Dict[str, Any]
    ):
        """
        缓存分类结果

        Args:
            title: 笔记标题
            content_hash: 内容的哈希值
            result: 分类结果
        """
        if not self.enabled:
            return

        cache_key = self._generate_cache_key({
            "type": "classification",
            "title": title,
            "content_hash": content_hash
        })

        self.classification_cache[cache_key] = result
        logger.debug(f"分类结果已缓存: {title[:50]}...")

    # ========== 缓存管理 ==========

    def clear_all(self):
        """清除所有缓存"""
        self.rag_cache.clear()
        self.vector_search_cache.clear()
        self.classification_cache.clear()
        logger.info("所有缓存已清除")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计数据
        """
        return {
            "enabled": self.enabled,
            "rag_cache": {
                "size": len(self.rag_cache),
                "maxsize": self.rag_cache.maxsize,
                "ttl": settings.CACHE_TTL_SECONDS
            },
            "vector_search_cache": {
                "size": len(self.vector_search_cache),
                "maxsize": self.vector_search_cache.maxsize
            },
            "classification_cache": {
                "size": len(self.classification_cache),
                "maxsize": self.classification_cache.maxsize
            }
        }


# 全局实例
cache_service = CacheService()
