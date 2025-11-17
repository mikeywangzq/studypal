"""
FastAPI Dependencies - 认证依赖
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from .database import get_db
from .services.auth_service import auth_service
from .models.user import User

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户

    Args:
        credentials: HTTP Bearer 认证凭证
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 认证失败时抛出
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 验证令牌
    token = credentials.credentials
    payload = auth_service.verify_token(token)

    if payload is None:
        raise credentials_exception

    # 获取用户ID
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    # 获取用户
    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户

    Args:
        current_user: 当前用户

    Returns:
        当前活跃用户对象

    Raises:
        HTTPException: 用户未激活时抛出
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    """
    获取可选的当前用户（不强制要求认证）

    Args:
        credentials: HTTP Bearer 认证凭证
        db: 数据库会话

    Returns:
        用户对象或 None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)

        if payload is None:
            return None

        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None

        user_id = UUID(user_id_str)
        user = auth_service.get_user_by_id(db, user_id)

        return user if user and user.is_active else None

    except Exception:
        return None
