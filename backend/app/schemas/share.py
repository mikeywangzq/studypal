"""
Note sharing schemas - 笔记分享相关的Pydantic模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class NoteShareCreate(BaseModel):
    """创建笔记分享"""
    shared_with: Optional[UUID] = Field(None, description="被分享者用户ID（null表示公开分享）")
    permission: str = Field("view", description="分享权限：view 或 edit")
    expires_at: Optional[datetime] = Field(None, description="过期时间（null表示永不过期）")


class NoteShareUpdate(BaseModel):
    """更新笔记分享"""
    permission: Optional[str] = Field(None, description="分享权限：view 或 edit")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    is_active: Optional[bool] = Field(None, description="是否激活")


class NoteShareResponse(BaseModel):
    """笔记分享响应"""
    id: UUID
    note_id: UUID
    shared_by: UUID
    shared_with: Optional[UUID]
    permission: str
    share_token: str
    expires_at: Optional[datetime]
    is_active: bool
    access_count: int
    last_accessed_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class NoteShareWithDetails(BaseModel):
    """笔记分享详情（包含用户和笔记信息）"""
    id: UUID
    note_id: UUID
    note_title: str
    shared_by: UUID
    shared_by_username: str
    shared_with: Optional[UUID]
    shared_with_username: Optional[str]
    permission: str
    share_token: str
    expires_at: Optional[datetime]
    is_active: bool
    access_count: int
    created_at: datetime


class NotePermissionCreate(BaseModel):
    """创建笔记权限"""
    user_id: UUID = Field(..., description="用户ID")
    permission_level: str = Field("viewer", description="权限级别：owner, editor, viewer")


class NotePermissionUpdate(BaseModel):
    """更新笔记权限"""
    permission_level: str = Field(..., description="权限级别：owner, editor, viewer")


class NotePermissionResponse(BaseModel):
    """笔记权限响应"""
    id: UUID
    note_id: UUID
    user_id: UUID
    permission_level: str
    granted_by: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class NotePermissionWithDetails(BaseModel):
    """笔记权限详情（包含用户信息）"""
    id: UUID
    note_id: UUID
    user_id: UUID
    username: str
    email: str
    permission_level: str
    granted_by: Optional[UUID]
    granted_by_username: Optional[str]
    created_at: datetime


class SharedNoteResponse(BaseModel):
    """分享给我的笔记响应"""
    note_id: UUID
    title: str
    category: Optional[str]
    tags: list[str]
    permission: str
    shared_by: UUID
    shared_by_username: str
    share_token: str
    created_at: datetime
    file_type: str
