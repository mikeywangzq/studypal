"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserWithToken,
    Token,
    UserProfileUpdate,
    PasswordChange,
    PasswordResetRequest,
    PasswordResetConfirm,
    OAuthLoginRequest,
)
from ..services.auth_service import auth_service
from ..services.oauth_service import oauth_service
from ..dependencies import get_current_active_user
from ..models.user import User
from ..config import settings

router = APIRouter()


@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册

    - **username**: 用户名（3-50个字符）
    - **email**: 邮箱地址
    - **password**: 密码（至少6个字符）

    返回用户信息和访问令牌
    """
    # 检查邮箱是否已存在
    existing_user = auth_service.get_user_by_email(db, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 检查用户名是否已存在
    existing_username = auth_service.get_user_by_username(db, user_create.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用"
        )

    # 创建用户
    user = auth_service.create_user(db, user_create)

    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )

    return UserWithToken(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/login", response_model=UserWithToken)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录

    - **email**: 邮箱地址
    - **password**: 密码

    返回用户信息和访问令牌
    """
    # 认证用户
    user = auth_service.authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )

    # 生成访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )

    return UserWithToken(
        user=UserResponse.model_validate(user),
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户信息

    需要在请求头中携带有效的访问令牌：
    ```
    Authorization: Bearer <access_token>
    ```
    """
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    刷新访问令牌

    使用当前有效的令牌获取新的访问令牌
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(current_user.id), "email": current_user.email},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新个人资料

    支持更新以下字段：
    - **username**: 用户名
    - **full_name**: 真实姓名
    - **bio**: 个人简介
    - **avatar_url**: 头像 URL

    所有字段均为可选，只更新提供的字段
    """
    # 检查用户名是否已被使用
    if profile_update.username:
        existing_user = auth_service.get_user_by_username(db, profile_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用"
            )

    updated_user = auth_service.update_user_profile(db, current_user.id, profile_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return UserResponse.model_validate(updated_user)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    修改密码

    需要提供当前密码进行验证
    """
    success = auth_service.change_password(
        db,
        current_user.id,
        password_change.current_password,
        password_change.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )

    return {"message": "密码修改成功"}


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    请求密码重置

    向注册邮箱发送重置令牌。
    **注意**：实际生产环境中，应该通过邮件发送令牌。
    此 MVP 版本直接返回令牌用于测试。
    """
    reset_token = auth_service.create_reset_token(db, reset_request.email)

    if not reset_token:
        # 为了安全，即使邮箱不存在也返回成功
        # 避免泄露用户邮箱是否已注册
        return {
            "message": "如果该邮箱已注册，重置链接已发送",
            "reset_token": None
        }

    # MVP 版本：直接返回令牌（生产环境应通过邮件发送）
    return {
        "message": "密码重置令牌已生成",
        "reset_token": reset_token,
        "note": "生产环境中此令牌应通过邮件发送，而非直接返回"
    }


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    确认密码重置

    使用重置令牌设置新密码
    """
    success = auth_service.reset_password(
        db,
        reset_confirm.reset_token,
        reset_confirm.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="重置令牌无效或已过期"
        )

    return {"message": "密码重置成功"}


@router.get("/oauth/{provider}/authorize")
async def oauth_authorize(provider: str, redirect_uri: str):
    """
    获取 OAuth 授权 URL

    支持的提供商：
    - **google**: Google OAuth
    - **github**: GitHub OAuth

    返回授权 URL，前端应重定向到该 URL
    """
    if provider not in ["google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的 OAuth 提供商"
        )

    auth_url = oauth_service.get_authorization_url(provider, redirect_uri)
    if not auth_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth 配置错误"
        )

    return {"authorization_url": auth_url}


@router.post("/oauth/login", response_model=UserWithToken)
async def oauth_login(
    oauth_request: OAuthLoginRequest,
    db: Session = Depends(get_db)
):
    """
    OAuth 登录

    使用授权码完成 OAuth 登录流程
    """
    if oauth_request.provider not in ["google", "github"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的 OAuth 提供商"
        )

    # 用授权码换取访问令牌
    access_token = await oauth_service.exchange_code_for_token(
        oauth_request.provider,
        oauth_request.code,
        oauth_request.redirect_uri
    )

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OAuth 授权失败"
        )

    # 获取用户信息
    user_info = await oauth_service.get_user_info(
        oauth_request.provider,
        access_token
    )

    if not user_info or not user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法获取用户信息"
        )

    # 获取或创建用户
    user = auth_service.get_or_create_oauth_user(
        db,
        email=user_info["email"],
        oauth_provider=oauth_request.provider,
        oauth_id=user_info["oauth_id"],
        username=user_info.get("username"),
        full_name=user_info.get("full_name"),
        avatar_url=user_info.get("avatar_url")
    )

    # 生成 JWT 令牌
    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=token_expires
    )

    return UserWithToken(
        user=UserResponse.model_validate(user),
        access_token=jwt_token,
        token_type="bearer"
    )
