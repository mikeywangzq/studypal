"""
Note Version History - 笔记版本历史模型
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..database import Base


class NoteVersion(Base):
    """笔记版本历史表"""

    __tablename__ = "note_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)

    # 版本信息
    version_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    tags = Column(String, nullable=True)  # JSON string

    # 变更信息
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    change_description = Column(Text, nullable=True)  # 可选的变更说明

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NoteComment(Base):
    """笔记评论表"""

    __tablename__ = "note_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 评论内容
    content = Column(Text, nullable=False)

    # 回复功能
    parent_id = Column(UUID(as_uuid=True), ForeignKey("note_comments.id", ondelete="CASCADE"), nullable=True, index=True)

    # 提及功能
    mentions = Column(String, nullable=True)  # JSON array of user IDs

    # 是否已编辑
    is_edited = Column(Boolean, default=False, nullable=False)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Notification(Base):
    """通知表"""

    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 通知类型
    type = Column(String(50), nullable=False, index=True)  # 'share', 'comment', 'mention', 'permission'

    # 通知内容
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)

    # 关联资源
    resource_type = Column(String(50), nullable=True)  # 'note', 'comment', 'share'
    resource_id = Column(UUID(as_uuid=True), nullable=True)

    # 发起者
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # 状态
    is_read = Column(Boolean, default=False, nullable=False, index=True)

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
