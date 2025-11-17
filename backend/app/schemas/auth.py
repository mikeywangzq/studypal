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


class UserLogin(BaseModel):
    """用户登录数据"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应数据"""
    id: UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


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
