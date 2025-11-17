"""
Collaboration schemas - 协作功能相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ========== 版本历史 ==========

class NoteVersionResponse(BaseModel):
    """笔记版本响应"""
    id: UUID
    note_id: UUID
    version_number: int
    title: str
    content: str
    category: Optional[str]
    tags: Optional[str]
    changed_by: Optional[UUID]
    change_description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class NoteVersionWithUser(BaseModel):
    """笔记版本详情（包含用户信息）"""
    id: UUID
    note_id: UUID
    version_number: int
    title: str
    content: str
    category: Optional[str]
    tags: List[str]
    changed_by: Optional[UUID]
    changed_by_username: Optional[str]
    change_description: Optional[str]
    created_at: datetime


class VersionCompareResponse(BaseModel):
    """版本对比响应"""
    old_version: NoteVersionWithUser
    new_version: NoteVersionWithUser
    differences: dict  # 包含变更的字段


# ========== 评论 ==========

class CommentCreate(BaseModel):
    """创建评论"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")
    parent_id: Optional[UUID] = Field(None, description="父评论ID（回复功能）")
    mentions: Optional[List[UUID]] = Field(None, description="提及的用户ID列表")


class CommentUpdate(BaseModel):
    """更新评论"""
    content: str = Field(..., min_length=1, max_length=2000, description="评论内容")


class CommentResponse(BaseModel):
    """评论响应"""
    id: UUID
    note_id: UUID
    user_id: UUID
    content: str
    parent_id: Optional[UUID]
    mentions: Optional[str]
    is_edited: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CommentWithUser(BaseModel):
    """评论详情（包含用户信息）"""
    id: UUID
    note_id: UUID
    user_id: UUID
    username: str
    avatar_url: Optional[str]
    content: str
    parent_id: Optional[UUID]
    mentions: List[UUID]
    is_edited: bool
    created_at: datetime
    updated_at: Optional[datetime]
    replies: List['CommentWithUser'] = []  # 嵌套回复


# ========== 通知 ==========

class NotificationCreate(BaseModel):
    """创建通知（内部使用）"""
    user_id: UUID
    type: str
    title: str
    message: str
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    actor_id: Optional[UUID] = None


class NotificationResponse(BaseModel):
    """通知响应"""
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    actor_id: Optional[UUID]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    model_config = {"from_attributes": True}


class NotificationWithActor(BaseModel):
    """通知详情（包含发起者信息）"""
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    actor_id: Optional[UUID]
    actor_username: Optional[str]
    actor_avatar_url: Optional[str]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]


class NotificationStats(BaseModel):
    """通知统计"""
    total: int
    unread: int
    by_type: dict  # 按类型统计


# ========== WebSocket 消息 ==========

class WSMessage(BaseModel):
    """WebSocket 消息"""
    type: str  # 'cursor', 'edit', 'join', 'leave'
    note_id: UUID
    user_id: UUID
    username: str
    data: dict  # 消息数据


class CursorPosition(BaseModel):
    """光标位置"""
    line: int
    column: int


class EditOperation(BaseModel):
    """编辑操作"""
    type: str  # 'insert', 'delete', 'replace'
    position: CursorPosition
    content: str
    length: Optional[int] = None
