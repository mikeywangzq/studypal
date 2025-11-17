"""
Note sharing models - 笔记分享模型
"""
from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from ..database import Base


class PermissionLevel(str, enum.Enum):
    """权限级别枚举"""
    OWNER = "owner"      # 所有者：完全控制
    EDITOR = "editor"    # 编辑者：可编辑
    VIEWER = "viewer"    # 查看者：只读


class SharePermission(str, enum.Enum):
    """分享权限枚举"""
    VIEW = "view"        # 仅查看
    EDIT = "edit"        # 可编辑


class NoteShare(Base):
    """笔记分享表 - 管理笔记的分享链接"""

    __tablename__ = "note_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    shared_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 被分享者 (null 表示公开分享，任何人都可访问)
    shared_with = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # 分享权限
    permission = Column(Enum(SharePermission), nullable=False, default=SharePermission.VIEW)

    # 分享令牌（用于链接分享）
    share_token = Column(String(64), unique=True, nullable=False, index=True)

    # 过期时间 (null 表示永不过期)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # 是否激活
    is_active = Column(Boolean, default=True, nullable=False)

    # 访问统计
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    # note = relationship("Note", back_populates="shares")
    # sharer = relationship("User", foreign_keys=[shared_by])
    # recipient = relationship("User", foreign_keys=[shared_with])


class NotePermission(Base):
    """笔记权限表 - 管理用户对笔记的访问权限"""

    __tablename__ = "note_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 权限级别
    permission_level = Column(Enum(PermissionLevel), nullable=False, default=PermissionLevel.VIEWER)

    # 权限授予者
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    # note = relationship("Note", back_populates="permissions")
    # user = relationship("User", foreign_keys=[user_id])
    # granter = relationship("User", foreign_keys=[granted_by])

    # 唯一约束：一个用户对一个笔记只能有一个权限
    __table_args__ = (
        UniqueConstraint('note_id', 'user_id', name='uq_note_user_permission'),
    )
