"""
Test Classification Service
"""
import pytest
from app.services.classification_service import ClassificationService


class TestClassificationService:
    """测试分类服务"""

    @pytest.fixture
    def classification_service(self):
        """创建分类服务实例"""
        return ClassificationService()

    def test_get_available_categories(self, classification_service):
        """测试获取可用分类列表"""
        categories = classification_service.get_available_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0
        assert "操作系统" in categories
        assert "计算机网络" in categories
        assert "数据库" in categories
        assert "算法与数据结构" in categories
        assert "其他" in categories

    @pytest.mark.asyncio
    async def test_classify_note_os(self, classification_service):
        """测试分类操作系统相关笔记"""
        title = "xv6_page_table.md"
        content = """
        # xv6 页表机制

        xv6 使用 RISC-V 的三级页表进行虚拟地址到物理地址的转换。

        ## 页表结构
        - 三级页表
        - 每级有 512 个 PTE
        - 每个 PTE 包含物理页号和标志位

        ## walk() 函数
        walk() 函数用于遍历页表，查找或创建页表项。
        """

        result = await classification_service.classify_note(
            title=title,
            content=content,
            file_type="md"
        )

        assert isinstance(result, dict)
        assert "category" in result
        assert "tags" in result
        assert "confidence" in result
        assert "reason" in result

        # 应该分类为操作系统
        assert result["category"] == "操作系统"

        # 应该有标签
        assert isinstance(result["tags"], list)
        assert len(result["tags"]) > 0

        # 置信度应该在有效范围内
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_classify_note_network(self, classification_service):
        """测试分类计算机网络相关笔记"""
        title = "tcp_handshake.md"
        content = """
        # TCP 三次握手

        TCP 协议使用三次握手建立连接。

        ## 握手过程
        1. SYN: 客户端发送 SYN 包
        2. SYN-ACK: 服务器响应 SYN-ACK 包
        3. ACK: 客户端发送 ACK 包

        ## TIME_WAIT 状态
        TIME_WAIT 状态持续 2MSL 时间，确保连接正常关闭。
        """

        result = await classification_service.classify_note(
            title=title,
            content=content,
            file_type="md"
        )

        # 应该分类为计算机网络
        assert result["category"] == "计算机网络"

        # 应该包含相关标签
        assert isinstance(result["tags"], list)
        tags_str = " ".join(result["tags"]).lower()
        # 至少包含一些网络相关的标签
        assert any(keyword in tags_str for keyword in ["tcp", "握手", "网络"])

    @pytest.mark.asyncio
    async def test_classify_note_database(self, classification_service):
        """测试分类数据库相关笔记"""
        title = "database_index.md"
        content = """
        # 数据库索引

        索引是提升数据库查询性能的关键。

        ## B+Tree 索引
        - 平衡树结构
        - 叶子节点存储数据
        - 支持范围查询

        ## 聚簇索引与非聚簇索引
        - 聚簇索引：数据按索引顺序存储
        - 非聚簇索引：索引和数据分开存储
        """

        result = await classification_service.classify_note(
            title=title,
            content=content,
            file_type="md"
        )

        # 应该分类为数据库
        assert result["category"] == "数据库"

        # 应该包含数据库相关标签
        assert isinstance(result["tags"], list)
        tags_str = " ".join(result["tags"]).lower()
        assert any(keyword in tags_str for keyword in ["索引", "b+tree", "数据库"])

    @pytest.mark.asyncio
    async def test_extract_tags_only(self, classification_service):
        """测试仅提取标签功能"""
        content = """
        Python 是一种高级编程语言，支持面向对象、函数式和过程式编程。
        常用的 Python 框架包括 Django、Flask、FastAPI 等。
        """

        tags = await classification_service.extract_tags_only(
            content=content,
            max_tags=5
        )

        assert isinstance(tags, list)
        assert len(tags) <= 5

        if len(tags) > 0:
            # 标签应该是字符串
            for tag in tags:
                assert isinstance(tag, str)
                assert len(tag) > 0

    @pytest.mark.asyncio
    async def test_classify_empty_content(self, classification_service):
        """测试分类空内容"""
        result = await classification_service.classify_note(
            title="empty.txt",
            content="",
            file_type="txt"
        )

        # 即使内容为空，也应该返回有效结果
        assert isinstance(result, dict)
        assert "category" in result
        assert "tags" in result

        # 可能返回"其他"分类
        assert result["category"] in classification_service.common_categories

    @pytest.mark.asyncio
    async def test_classify_long_content(self, classification_service):
        """测试分类长内容（测试截断逻辑）"""
        # 创建一个超过2000字符的内容
        long_content = "操作系统进程管理\n" * 200

        result = await classification_service.classify_note(
            title="long_note.md",
            content=long_content,
            file_type="md"
        )

        # 应该正常处理（内部会截断）
        assert isinstance(result, dict)
        assert "category" in result

    def test_categories_uniqueness(self, classification_service):
        """测试分类列表中没有重复项"""
        categories = classification_service.get_available_categories()
        assert len(categories) == len(set(categories))

    def test_categories_not_empty_strings(self, classification_service):
        """测试所有分类都不是空字符串"""
        categories = classification_service.get_available_categories()
        for category in categories:
            assert isinstance(category, str)
            assert len(category) > 0
