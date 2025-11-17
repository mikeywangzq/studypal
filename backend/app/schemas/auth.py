"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """用户注册数据"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")


class UserLogin(BaseModel):
    """用户登录数据"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应数据"""
    id: UUID
    username: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    oauth_provider: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    """用户个人资料更新"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")


class PasswordChange(BaseModel):
    """密码修改"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    email: EmailStr = Field(..., description="注册邮箱")


class PasswordResetConfirm(BaseModel):
    """密码重置确认"""
    reset_token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[str] = None
    email: Optional[str] = None


class UserWithToken(BaseModel):
    """用户信息和令牌"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class OAuthLoginRequest(BaseModel):
    """OAuth 登录请求"""
    provider: str = Field(..., description="OAuth 提供商（google, github）")
    code: str = Field(..., description="授权码")
    redirect_uri: str = Field(..., description="回调地址")
