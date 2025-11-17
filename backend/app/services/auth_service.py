"""
Authentication Service - JWT 用户认证服务
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import uuid

from ..models.user import User
from ..schemas.auth import UserCreate
from ..config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码

        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码

        Returns:
            密码是否正确
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        生成密码哈希

        Args:
            password: 明文密码

        Returns:
            哈希密码
        """
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌

        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量

        Returns:
            JWT 访问令牌
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        验证令牌

        Args:
            token: JWT 令牌

        Returns:
            解码后的数据，验证失败返回 None
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        通过邮箱获取用户

        Args:
            db: 数据库会话
            email: 用户邮箱

        Returns:
            用户对象，不存在返回 None
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        通过用户名获取用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            用户对象，不存在返回 None
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """
        通过ID获取用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户对象，不存在返回 None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """
        创建用户

        Args:
            db: 数据库会话
            user_create: 用户创建数据

        Returns:
            创建的用户对象
        """
        # 生成密码哈希
        hashed_password = AuthService.get_password_hash(user_create.password)

        # 创建用户
        user = User(
            id=uuid.uuid4(),
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            is_active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        认证用户

        Args:
            db: 数据库会话
            email: 用户邮箱
            password: 密码

        Returns:
            认证成功返回用户对象，失败返回 None
        """
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user


# 全局实例
auth_service = AuthService()
