"""
Note Sharing Service - 笔记分享服务
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
import secrets

from ..models.note_share import NoteShare, NotePermission, SharePermission, PermissionLevel
from ..models.note import Note
from ..models.user import User
from ..schemas.share import (
    NoteShareCreate,
    NoteShareUpdate,
    NotePermissionCreate,
    NotePermissionUpdate,
)


class ShareService:
    """笔记分享服务"""

    @staticmethod
    def generate_share_token() -> str:
        """
        生成安全的分享令牌

        Returns:
            32字节的URL安全随机字符串
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_share(
        db: Session,
        note_id: UUID,
        user_id: UUID,
        share_create: NoteShareCreate
    ) -> Optional[NoteShare]:
        """
        创建笔记分享

        Args:
            db: 数据库会话
            note_id: 笔记ID
            user_id: 分享者ID
            share_create: 分享创建数据

        Returns:
            创建的分享对象
        """
        # 检查笔记是否存在且用户有权限
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return None

        # 检查用户是否是笔记所有者或有编辑权限
        if note.user_id != user_id:
            permission = ShareService.get_user_permission(db, note_id, user_id)
            if not permission or permission.permission_level not in [PermissionLevel.OWNER, PermissionLevel.EDITOR]:
                return None

        # 验证分享权限
        if share_create.permission not in ['view', 'edit']:
            return None

        # 生成分享令牌
        share_token = ShareService.generate_share_token()

        # 创建分享
        share = NoteShare(
            note_id=note_id,
            shared_by=user_id,
            shared_with=share_create.shared_with,
            permission=SharePermission(share_create.permission),
            share_token=share_token,
            expires_at=share_create.expires_at,
            is_active=True
        )

        db.add(share)
        db.commit()
        db.refresh(share)

        return share

    @staticmethod
    def get_note_shares(
        db: Session,
        note_id: UUID,
        user_id: UUID
    ) -> List[NoteShare]:
        """
        获取笔记的所有分享

        Args:
            db: 数据库会话
            note_id: 笔记ID
            user_id: 请求用户ID

        Returns:
            分享列表
        """
        # 检查用户是否有权限查看分享列表
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note or note.user_id != user_id:
            return []

        return db.query(NoteShare).filter(
            NoteShare.note_id == note_id
        ).order_by(NoteShare.created_at.desc()).all()

    @staticmethod
    def get_share_by_id(db: Session, share_id: UUID) -> Optional[NoteShare]:
        """
        通过ID获取分享

        Args:
            db: 数据库会话
            share_id: 分享ID

        Returns:
            分享对象或None
        """
        return db.query(NoteShare).filter(NoteShare.id == share_id).first()

    @staticmethod
    def get_share_by_token(
        db: Session,
        share_token: str
    ) -> Optional[NoteShare]:
        """
        通过令牌获取分享

        Args:
            db: 数据库会话
            share_token: 分享令牌

        Returns:
            分享对象或None
        """
        share = db.query(NoteShare).filter(
            NoteShare.share_token == share_token
        ).first()

        if not share:
            return None

        # 检查分享是否激活
        if not share.is_active:
            return None

        # 检查是否过期
        if share.expires_at and share.expires_at < datetime.utcnow():
            return None

        # 更新访问统计
        share.access_count += 1
        share.last_accessed_at = datetime.utcnow()
        db.commit()

        return share

    @staticmethod
    def update_share(
        db: Session,
        share_id: UUID,
        user_id: UUID,
        share_update: NoteShareUpdate
    ) -> Optional[NoteShare]:
        """
        更新分享

        Args:
            db: 数据库会话
            share_id: 分享ID
            user_id: 用户ID
            share_update: 更新数据

        Returns:
            更新后的分享对象
        """
        share = db.query(NoteShare).filter(NoteShare.id == share_id).first()
        if not share or share.shared_by != user_id:
            return None

        # 更新非空字段
        update_data = share_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'permission' and value not in ['view', 'edit']:
                continue
            if field == 'permission':
                value = SharePermission(value)
            setattr(share, field, value)

        db.commit()
        db.refresh(share)

        return share

    @staticmethod
    def delete_share(
        db: Session,
        share_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        删除分享

        Args:
            db: 数据库会话
            share_id: 分享ID
            user_id: 用户ID

        Returns:
            是否成功
        """
        share = db.query(NoteShare).filter(NoteShare.id == share_id).first()
        if not share or share.shared_by != user_id:
            return False

        db.delete(share)
        db.commit()

        return True

    @staticmethod
    def get_shared_with_me(
        db: Session,
        user_id: UUID
    ) -> List[NoteShare]:
        """
        获取分享给我的笔记

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            分享列表
        """
        now = datetime.utcnow()

        return db.query(NoteShare).filter(
            and_(
                NoteShare.shared_with == user_id,
                NoteShare.is_active == True,
                or_(
                    NoteShare.expires_at == None,
                    NoteShare.expires_at > now
                )
            )
        ).order_by(NoteShare.created_at.desc()).all()

    # ========== 权限管理 ==========

    @staticmethod
    def create_permission(
        db: Session,
        note_id: UUID,
        granter_id: UUID,
        permission_create: NotePermissionCreate
    ) -> Optional[NotePermission]:
        """
        创建笔记权限

        Args:
            db: 数据库会话
            note_id: 笔记ID
            granter_id: 授权者ID
            permission_create: 权限创建数据

        Returns:
            创建的权限对象
        """
        # 检查笔记是否存在
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return None

        # 检查授权者是否是所有者
        if note.user_id != granter_id:
            return None

        # 验证权限级别
        if permission_create.permission_level not in ['owner', 'editor', 'viewer']:
            return None

        # 检查是否已存在权限
        existing = db.query(NotePermission).filter(
            and_(
                NotePermission.note_id == note_id,
                NotePermission.user_id == permission_create.user_id
            )
        ).first()

        if existing:
            # 更新现有权限
            existing.permission_level = PermissionLevel(permission_create.permission_level)
            existing.granted_by = granter_id
            db.commit()
            db.refresh(existing)
            return existing

        # 创建新权限
        permission = NotePermission(
            note_id=note_id,
            user_id=permission_create.user_id,
            permission_level=PermissionLevel(permission_create.permission_level),
            granted_by=granter_id
        )

        db.add(permission)
        db.commit()
        db.refresh(permission)

        return permission

    @staticmethod
    def get_note_permissions(
        db: Session,
        note_id: UUID,
        user_id: UUID
    ) -> List[NotePermission]:
        """
        获取笔记的所有权限

        Args:
            db: 数据库会话
            note_id: 笔记ID
            user_id: 请求用户ID

        Returns:
            权限列表
        """
        # 检查用户是否有权限查看
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note or note.user_id != user_id:
            return []

        return db.query(NotePermission).filter(
            NotePermission.note_id == note_id
        ).order_by(NotePermission.created_at.desc()).all()

    @staticmethod
    def get_user_permission(
        db: Session,
        note_id: UUID,
        user_id: UUID
    ) -> Optional[NotePermission]:
        """
        获取用户对笔记的权限

        Args:
            db: 数据库会话
            note_id: 笔记ID
            user_id: 用户ID

        Returns:
            权限对象或None
        """
        return db.query(NotePermission).filter(
            and_(
                NotePermission.note_id == note_id,
                NotePermission.user_id == user_id
            )
        ).first()

    @staticmethod
    def delete_permission(
        db: Session,
        permission_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        删除权限

        Args:
            db: 数据库会话
            permission_id: 权限ID
            user_id: 用户ID

        Returns:
            是否成功
        """
        permission = db.query(NotePermission).filter(
            NotePermission.id == permission_id
        ).first()

        if not permission:
            return False

        # 检查用户是否是笔记所有者
        note = db.query(Note).filter(Note.id == permission.note_id).first()
        if not note or note.user_id != user_id:
            return False

        db.delete(permission)
        db.commit()

        return True

    @staticmethod
    def check_user_access(
        db: Session,
        note_id: UUID,
        user_id: UUID,
        required_permission: str = 'view'
    ) -> bool:
        """
        检查用户是否有权限访问笔记

        Args:
            db: 数据库会话
            note_id: 笔记ID
            user_id: 用户ID
            required_permission: 所需权限 ('view' 或 'edit')

        Returns:
            是否有权限
        """
        # 检查是否是所有者
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return False

        if note.user_id == user_id:
            return True

        # 检查直接权限
        permission = ShareService.get_user_permission(db, note_id, user_id)
        if permission:
            if required_permission == 'view':
                return True
            if required_permission == 'edit' and permission.permission_level in [PermissionLevel.OWNER, PermissionLevel.EDITOR]:
                return True

        # 检查分享权限
        now = datetime.utcnow()
        share = db.query(NoteShare).filter(
            and_(
                NoteShare.note_id == note_id,
                NoteShare.shared_with == user_id,
                NoteShare.is_active == True,
                or_(
                    NoteShare.expires_at == None,
                    NoteShare.expires_at > now
                )
            )
        ).first()

        if share:
            if required_permission == 'view':
                return True
            if required_permission == 'edit' and share.permission == SharePermission.EDIT:
                return True

        return False


# 全局实例
share_service = ShareService()
