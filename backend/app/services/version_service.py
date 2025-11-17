"""
Version Control Service - 版本控制服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import json

from ..models.note_version import NoteVersion
from ..models.note import Note
from ..models.user import User


class VersionService:
    """版本控制服务"""

    @staticmethod
    def create_version(
        db: Session,
        note_id: UUID,
        changed_by: UUID,
        change_description: Optional[str] = None
    ) -> NoteVersion:
        """
        创建笔记版本快照

        Args:
            db: 数据库会话
            note_id: 笔记ID
            changed_by: 修改者ID
            change_description: 变更说明

        Returns:
            创建的版本对象
        """
        # 获取当前笔记
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return None

        # 获取最新版本号
        latest_version = db.query(NoteVersion).filter(
            NoteVersion.note_id == note_id
        ).order_by(NoteVersion.version_number.desc()).first()

        version_number = (latest_version.version_number + 1) if latest_version else 1

        # 创建版本快照
        version = NoteVersion(
            note_id=note_id,
            version_number=version_number,
            title=note.title,
            content=note.content,
            category=note.category,
            tags=json.dumps(note.tags) if note.tags else None,
            changed_by=changed_by,
            change_description=change_description
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        return version

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
            return False

        # 获取笔记
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return False

        # 先创建当前版本快照
        VersionService.create_version(
            db,
            note_id,
            user_id,
            f"恢复到版本 {version.version_number}"
        )

        # 恢复笔记内容
        note.title = version.title
        note.content = version.content
        note.category = version.category
        note.tags = json.loads(version.tags) if version.tags else None

        db.commit()

        return True

    @staticmethod
    def compare_versions(
        db: Session,
        version_id1: UUID,
        version_id2: UUID
    ) -> Optional[dict]:
        """
        对比两个版本

        Args:
            db: 数据库会话
            version_id1: 版本1 ID
            version_id2: 版本2 ID

        Returns:
            对比结果字典
        """
        version1 = VersionService.get_version_by_id(db, version_id1)
        version2 = VersionService.get_version_by_id(db, version_id2)

        if not version1 or not version2:
            return None

        if version1.note_id != version2.note_id:
            return None

        # 对比字段
        differences = {}

        if version1.title != version2.title:
            differences['title'] = {
                'old': version1.title,
                'new': version2.title
            }

        if version1.content != version2.content:
            differences['content'] = {
                'old': version1.content,
                'new': version2.content
            }

        if version1.category != version2.category:
            differences['category'] = {
                'old': version1.category,
                'new': version2.category
            }

        if version1.tags != version2.tags:
            differences['tags'] = {
                'old': json.loads(version1.tags) if version1.tags else [],
                'new': json.loads(version2.tags) if version2.tags else []
            }

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
