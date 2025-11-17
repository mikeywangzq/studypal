"""
Note Version History - 笔记版本历史模型
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from ..database import Base


class NoteVersion(Base):
    """
    笔记版本历史表

    使用快照机制存储每个版本的完整内容，便于快速恢复和对比
    版本号从1开始递增，每次创建新版本时自动+1
    """

    __tablename__ = "note_versions"

    # 主键和外键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="版本唯一标识")
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联的笔记ID")

    # 版本信息（快照内容）
    version_number = Column(Integer, nullable=False, comment="版本号，从1开始递增")
    title = Column(String, nullable=False, comment="笔记标题快照")
    content = Column(Text, nullable=False, comment="笔记内容快照")
    category = Column(String, nullable=True, comment="笔记分类快照")
    tags = Column(String, nullable=True, comment="笔记标签快照（JSON字符串数组）")

    # 变更信息
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="版本创建者ID")
    change_description = Column(Text, nullable=True, comment="可选的变更说明，描述此版本做了什么修改")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="版本创建时间")


class NoteComment(Base):
    """
    笔记评论表

    支持嵌套回复和@提及功能
    - 通过parent_id实现评论的树形结构（一层回复）
    - 通过mentions字段支持@提及多个用户
    - 级联删除：删除笔记时删除所有评论，删除父评论时删除所有子评论
    """

    __tablename__ = "note_comments"

    # 主键和外键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="评论唯一标识")
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联的笔记ID")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="评论作者ID")

    # 评论内容
    content = Column(Text, nullable=False, comment="评论文本内容")

    # 回复功能（支持嵌套评论）
    parent_id = Column(UUID(as_uuid=True), ForeignKey("note_comments.id", ondelete="CASCADE"), nullable=True, index=True, comment="父评论ID，为NULL表示顶层评论")

    # 提及功能（@用户）
    mentions = Column(String, nullable=True, comment="被提及的用户ID列表（JSON字符串数组）")

    # 编辑状态
    is_edited = Column(Boolean, default=False, nullable=False, comment="是否已被编辑过")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="评论创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="评论最后更新时间")


class Notification(Base):
    """
    通知表

    支持四种通知类型：
    1. share - 笔记分享通知
    2. comment - 评论通知
    3. mention - @提及通知
    4. permission - 权限变更通知

    设计要点：
    - 通过resource_type和resource_id关联相关资源
    - actor_id记录通知的发起者
    - is_read用于已读/未读状态管理
    - 级联删除：删除用户时删除该用户的所有通知
    """

    __tablename__ = "notifications"

    # 主键和外键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="通知唯一标识")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="接收通知的用户ID")

    # 通知类型（添加索引提高查询性能）
    type = Column(String(50), nullable=False, index=True, comment="通知类型：share|comment|mention|permission")

    # 通知内容
    title = Column(String(200), nullable=False, comment="通知标题")
    message = Column(Text, nullable=False, comment="通知消息内容")

    # 关联资源（可选，指向触发通知的资源）
    resource_type = Column(String(50), nullable=True, comment="资源类型：note|comment|share")
    resource_id = Column(UUID(as_uuid=True), nullable=True, comment="资源ID")

    # 发起者（触发通知的用户）
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="通知发起者ID")

    # 状态（添加索引以快速查询未读通知）
    is_read = Column(Boolean, default=False, nullable=False, index=True, comment="是否已读")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="通知创建时间")
    read_at = Column(DateTime(timezone=True), nullable=True, comment="通知已读时间")
