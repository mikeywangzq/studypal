"""
Classification Service - 使用 LLM 进行笔记自动分类和标签提取
"""
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class ClassificationService:
    """笔记分类和标签提取服务"""

    def __init__(self):
        """初始化 LLM"""
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,  # 较低温度以获得更稳定的分类结果
            openai_api_key=settings.OPENAI_API_KEY,
        )

        # 预定义的常见分类（可以根据实际情况调整）
        self.common_categories = [
            "操作系统",
            "计算机网络",
            "数据库",
            "算法与数据结构",
            "编程语言",
            "软件工程",
            "计算机体系结构",
            "人工智能",
            "机器学习",
            "Web开发",
            "移动开发",
            "云计算",
            "网络安全",
            "其他",
        ]

    async def classify_note(
        self, title: str, content: str, file_type: str
    ) -> Dict[str, any]:
        """
        自动分类笔记并提取标签

        Args:
            title: 笔记标题
            content: 笔记内容（截取前2000字符）
            file_type: 文件类型

        Returns:
            {
                "category": "推荐的分类",
                "tags": ["标签1", "标签2", ...],
                "confidence": 0.95,  # 置信度 (0-1)
                "reason": "分类理由"
            }
        """
        try:
            # 截取内容前2000字符，避免token过多
            content_preview = content[:2000] if len(content) > 2000 else content

            # 构建提示词
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """你是一个专业的计算机科学笔记分类助手。你的任务是：
1. 根据笔记的标题和内容，推荐一个最合适的分类
2. 提取3-7个关键标签（技术术语、概念、工具等）
3. 评估分类的置信度（0-1之间的小数）
4. 简要说明分类理由

可选的分类包括：{categories}

请以JSON格式返回结果：
{{
    "category": "分类名称",
    "tags": ["标签1", "标签2", "标签3"],
    "confidence": 0.95,
    "reason": "简短的分类理由"
}}

注意：
- 标签应该是具体的技术术语，如"TCP"、"B+Tree"、"页表"等
- 标签使用中文，除非是专业术语的英文缩写
- 如果内容不属于任何预定义分类，使用"其他"
- 确保返回的是有效的JSON格式""",
                    ),
                    (
                        "user",
                        """文件类型: {file_type}
标题: {title}

内容预览:
{content}

请分析并返回分类结果。""",
                    ),
                ]
            )

            # 调用 LLM
            messages = prompt.format_messages(
                categories=", ".join(self.common_categories),
                file_type=file_type,
                title=title,
                content=content_preview,
            )

            response = await self.llm.ainvoke(messages)
            result_text = response.content.strip()

            # 尝试提取JSON（有时LLM会在JSON前后添加说明文字）
            if "```json" in result_text:
                # 提取代码块中的JSON
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                # 提取代码块中的JSON
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()

            # 解析JSON
            result = json.loads(result_text)

            # 验证和清理结果
            category = result.get("category", "其他")
            tags = result.get("tags", [])
            confidence = float(result.get("confidence", 0.8))
            reason = result.get("reason", "基于内容分析")

            # 确保分类在预定义列表中
            if category not in self.common_categories:
                category = "其他"

            # 限制标签数量
            tags = tags[:7] if isinstance(tags, list) else []

            # 确保置信度在有效范围内
            confidence = max(0.0, min(1.0, confidence))

            logger.info(
                f"笔记分类完成: '{title}' -> {category} (置信度: {confidence:.2f})"
            )

            return {
                "category": category,
                "tags": tags,
                "confidence": confidence,
                "reason": reason,
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始响应: {result_text}")
            # 返回默认结果
            return {
                "category": "其他",
                "tags": [],
                "confidence": 0.5,
                "reason": "自动分类失败，请手动设置",
            }

        except Exception as e:
            logger.error(f"笔记分类失败: {e}")
            # 返回默认结果
            return {
                "category": "其他",
                "tags": [],
                "confidence": 0.5,
                "reason": f"分类错误: {str(e)}",
            }

    async def extract_tags_only(self, content: str, max_tags: int = 5) -> List[str]:
        """
        仅提取标签（不进行分类）

        Args:
            content: 文本内容
            max_tags: 最大标签数量

        Returns:
            标签列表
        """
        try:
            content_preview = content[:1500] if len(content) > 1500 else content

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        f"""你是一个标签提取助手。从给定的文本中提取{max_tags}个最重要的技术关键词作为标签。

要求：
- 标签应该是技术术语、概念、工具名称等
- 优先选择专业术语和核心概念
- 标签使用中文，专业术语可以用英文缩写
- 每个标签2-8个字

请以JSON数组格式返回：["标签1", "标签2", "标签3"]""",
                    ),
                    ("user", "内容:\n{content}\n\n请提取关键标签。"),
                ]
            )

            messages = prompt.format_messages(content=content_preview)
            response = await self.llm.ainvoke(messages)
            result_text = response.content.strip()

            # 提取JSON数组
            if "[" in result_text and "]" in result_text:
                json_start = result_text.find("[")
                json_end = result_text.rfind("]") + 1
                result_text = result_text[json_start:json_end]

            tags = json.loads(result_text)

            if isinstance(tags, list):
                return tags[:max_tags]
            else:
                return []

        except Exception as e:
            logger.error(f"标签提取失败: {e}")
            return []

    def get_available_categories(self) -> List[str]:
        """获取所有可用的分类"""
        return self.common_categories.copy()


# 全局实例
classification_service = ClassificationService()
