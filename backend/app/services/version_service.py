"""
Version Control Service - 版本控制服务

提供笔记版本管理功能：
- 创建版本快照
- 获取版本历史
- 版本对比
- 版本回滚
- 清理旧版本
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import json
import logging

from ..models.note_version import NoteVersion
from ..models.note import Note
from ..models.user import User

# 配置日志
logger = logging.getLogger(__name__)


class VersionService:
    """
    版本控制服务类

    采用快照机制而非差分存储，优点：
    1. 实现简单，恢复迅速
    2. 无需计算差分，性能稳定
    3. 版本独立，不依赖其他版本

    缺点：
    - 存储空间占用较大（可通过定期清理旧版本缓解）
    """

    @staticmethod
    def create_version(
        db: Session,
        note_id: UUID,
        changed_by: UUID,
        change_description: Optional[str] = None
    ) -> Optional[NoteVersion]:
        """
        创建笔记版本快照

        流程：
        1. 获取笔记当前状态
        2. 查询最新版本号并递增
        3. 创建快照记录（包含title、content、category、tags）
        4. 保存到数据库

        Args:
            db: 数据库会话
            note_id: 笔记ID
            changed_by: 修改者ID（谁创建的这个版本）
            change_description: 可选的变更说明（描述本次修改内容）

        Returns:
            创建的版本对象，如果笔记不存在则返回None
        """
        # 获取当前笔记
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            logger.warning(f"笔记不存在，无法创建版本: note_id={note_id}")
            return None

        try:
            # 获取最新版本号（按版本号降序排列，取第一个）
            latest_version = db.query(NoteVersion).filter(
                NoteVersion.note_id == note_id
            ).order_by(NoteVersion.version_number.desc()).first()

            # 版本号从1开始递增
            version_number = (latest_version.version_number + 1) if latest_version else 1

            # 创建版本快照（存储笔记的完整状态）
            version = NoteVersion(
                note_id=note_id,
                version_number=version_number,
                title=note.title,
                content=note.content,
                category=note.category,
                tags=json.dumps(note.tags, ensure_ascii=False) if note.tags else None,  # 支持中文标签
                changed_by=changed_by,
                change_description=change_description
            )

            db.add(version)
            db.commit()
            db.refresh(version)

            logger.info(f"成功创建版本快照: note_id={note_id}, version={version_number}")
            return version

        except Exception as e:
            logger.error(f"创建版本快照失败: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_note_versions(
        db: Session,
        note_id: UUID,
        limit: int = 50
    ) -> List[NoteVersion]:
        """
        获取笔记的所有版本

        Args:
            db: 数据库会话
            note_id: 笔记ID
            limit: 返回数量限制

        Returns:
            版本列表（按时间倒序）
        """
        return db.query(NoteVersion).filter(
            NoteVersion.note_id == note_id
        ).order_by(NoteVersion.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_version_by_id(
        db: Session,
        version_id: UUID
    ) -> Optional[NoteVersion]:
        """
        通过ID获取版本

        Args:
            db: 数据库会话
            version_id: 版本ID

        Returns:
            版本对象或None
        """
        return db.query(NoteVersion).filter(NoteVersion.id == version_id).first()

    @staticmethod
    def get_version_by_number(
        db: Session,
        note_id: UUID,
        version_number: int
    ) -> Optional[NoteVersion]:
        """
        通过版本号获取版本

        Args:
            db: 数据库会话
            note_id: 笔记ID
            version_number: 版本号

        Returns:
            版本对象或None
        """
        return db.query(NoteVersion).filter(
            NoteVersion.note_id == note_id,
            NoteVersion.version_number == version_number
        ).first()

    @staticmethod
    def restore_version(
        db: Session,
        note_id: UUID,
        version_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        恢复到指定版本

        流程：
        1. 检查版本和笔记是否存在
        2. 创建当前状态的快照（避免数据丢失）
        3. 恢复笔记到指定版本的内容
        4. 提交数据库事务

        Args:
            db: 数据库会话
            note_id: 笔记ID
            version_id: 要恢复的版本ID
            user_id: 操作用户ID

        Returns:
            是否成功
        """
        # 获取版本
        version = VersionService.get_version_by_id(db, version_id)
        if not version or version.note_id != note_id:
            logger.warning(f"版本不存在或不匹配: version_id={version_id}, note_id={note_id}")
            return False

        # 获取笔记
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            logger.warning(f"笔记不存在: note_id={note_id}")
            return False

        # 先创建当前版本快照（防止误操作导致数据丢失）
        try:
            VersionService.create_version(
                db,
                note_id,
                user_id,
                f"恢复到版本 {version.version_number} 前的备份"
            )
        except Exception as e:
            logger.error(f"创建备份快照失败: {e}")
            return False

        # 恢复笔记内容
        try:
            note.title = version.title
            note.content = version.content
            note.category = version.category

            # 安全地解析JSON标签（添加异常处理）
            if version.tags:
                try:
                    note.tags = json.loads(version.tags)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}, tags={version.tags}")
                    note.tags = []
            else:
                note.tags = []

            db.commit()
            logger.info(f"成功恢复笔记 {note_id} 到版本 {version.version_number}")
            return True

        except Exception as e:
            logger.error(f"恢复版本时发生错误: {e}")
            db.rollback()
            return False

    @staticmethod
    def compare_versions(
        db: Session,
        version_id1: UUID,
        version_id2: UUID
    ) -> Optional[dict]:
        """
        对比两个版本的差异

        比较内容包括：
        - title: 标题
        - content: 正文内容
        - category: 分类
        - tags: 标签数组

        Args:
            db: 数据库会话
            version_id1: 旧版本ID（通常是较早的版本）
            version_id2: 新版本ID（通常是较新的版本）

        Returns:
            包含两个版本信息和差异字典的结果，格式：
            {
                'version1': NoteVersion对象,
                'version2': NoteVersion对象,
                'differences': {
                    'title': {'old': '旧标题', 'new': '新标题'},
                    'content': {'old': '旧内容', 'new': '新内容'},
                    ...
                }
            }
            如果版本不存在或不属于同一笔记则返回None
        """
        # 获取两个版本
        version1 = VersionService.get_version_by_id(db, version_id1)
        version2 = VersionService.get_version_by_id(db, version_id2)

        if not version1 or not version2:
            logger.warning(f"版本不存在: v1={version_id1}, v2={version_id2}")
            return None

        # 检查两个版本是否属于同一笔记
        if version1.note_id != version2.note_id:
            logger.warning(f"版本不属于同一笔记: v1.note={version1.note_id}, v2.note={version2.note_id}")
            return None

        # 对比各个字段
        differences = {}

        # 对比标题
        if version1.title != version2.title:
            differences['title'] = {
                'old': version1.title,
                'new': version2.title
            }

        # 对比内容
        if version1.content != version2.content:
            differences['content'] = {
                'old': version1.content,
                'new': version2.content
            }

        # 对比分类
        if version1.category != version2.category:
            differences['category'] = {
                'old': version1.category,
                'new': version2.category
            }

        # 对比标签（安全解析JSON）
        if version1.tags != version2.tags:
            try:
                old_tags = json.loads(version1.tags) if version1.tags else []
                new_tags = json.loads(version2.tags) if version2.tags else []
                differences['tags'] = {
                    'old': old_tags,
                    'new': new_tags
                }
            except json.JSONDecodeError as e:
                logger.error(f"标签JSON解析失败: {e}")
                differences['tags'] = {
                    'old': [],
                    'new': []
                }

        logger.info(f"版本对比完成: {len(differences)} 个字段有差异")

        return {
            'version1': version1,
            'version2': version2,
            'differences': differences
        }

    @staticmethod
    def delete_old_versions(
        db: Session,
        note_id: UUID,
        keep_count: int = 20
    ) -> int:
        """
        删除旧版本（保留最新的N个）

        Args:
            db: 数据库会话
            note_id: 笔记ID
            keep_count: 保留版本数

        Returns:
            删除的版本数
        """
        versions = db.query(NoteVersion).filter(
            NoteVersion.note_id == note_id
        ).order_by(NoteVersion.created_at.desc()).offset(keep_count).all()

        delete_count = len(versions)

        for version in versions:
            db.delete(version)

        db.commit()

        return delete_count


# 全局实例
version_service = VersionService()
