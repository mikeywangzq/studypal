"""
Authentication Service - JWT 用户认证服务
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import uuid
import secrets

from ..models.user import User
from ..schemas.auth import UserCreate, UserProfileUpdate
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
        password_hash = AuthService.get_password_hash(user_create.password)

        # 创建用户
        user = User(
            id=uuid.uuid4(),
            username=user_create.username,
            email=user_create.email,
            password_hash=password_hash,
            full_name=user_create.full_name,
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
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: uuid.UUID,
        profile_update: UserProfileUpdate
    ) -> Optional[User]:
        """
        更新用户个人资料

        Args:
            db: 数据库会话
            user_id: 用户 ID
            profile_update: 个人资料更新数据

        Returns:
            更新后的用户对象
        """
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            return None

        # 更新非空字段
        update_data = profile_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(
        db: Session,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        修改密码

        Args:
            db: 数据库会话
            user_id: 用户 ID
            current_password: 当前密码
            new_password: 新密码

        Returns:
            是否成功
        """
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            return False

        # 验证当前密码
        if not AuthService.verify_password(current_password, user.password_hash):
            return False

        # 更新密码
        user.password_hash = AuthService.get_password_hash(new_password)
        db.commit()
        return True

    @staticmethod
    def create_reset_token(db: Session, email: str) -> Optional[str]:
        """
        创建密码重置令牌

        Args:
            db: 数据库会话
            email: 邮箱

        Returns:
            重置令牌或 None
        """
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None

        # 生成安全的随机令牌
        reset_token = secrets.token_urlsafe(32)

        # 设置令牌和过期时间（1小时）
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)

        db.commit()
        return reset_token

    @staticmethod
    def reset_password(
        db: Session,
        reset_token: str,
        new_password: str
    ) -> bool:
        """
        通过令牌重置密码

        Args:
            db: 数据库会话
            reset_token: 重置令牌
            new_password: 新密码

        Returns:
            是否成功
        """
        user = db.query(User).filter(User.reset_token == reset_token).first()
        if not user:
            return False

        # 检查令牌是否过期
        if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return False

        # 更新密码并清除重置令牌
        user.password_hash = AuthService.get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None

        db.commit()
        return True

    @staticmethod
    def get_or_create_oauth_user(
        db: Session,
        email: str,
        oauth_provider: str,
        oauth_id: str,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> User:
        """
        获取或创建 OAuth 用户

        Args:
            db: 数据库会话
            email: 邮箱
            oauth_provider: OAuth 提供商
            oauth_id: OAuth 用户 ID
            username: 用户名（可选）
            full_name: 真实姓名（可选）
            avatar_url: 头像URL（可选）

        Returns:
            用户对象
        """
        # 首先尝试通过 OAuth ID 查找
        user = db.query(User).filter(
            User.oauth_provider == oauth_provider,
            User.oauth_id == oauth_id
        ).first()

        if user:
            return user

        # 其次尝试通过邮箱查找
        user = AuthService.get_user_by_email(db, email)
        if user:
            # 绑定 OAuth 信息
            user.oauth_provider = oauth_provider
            user.oauth_id = oauth_id
            if avatar_url and not user.avatar_url:
                user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)
            return user

        # 创建新用户
        if not username:
            username = email.split('@')[0]

        # 确保用户名唯一
        base_username = username
        counter = 1
        while AuthService.get_user_by_username(db, username):
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            email=email,
            password_hash=AuthService.get_password_hash(secrets.token_urlsafe(32)),  # 随机密码
            full_name=full_name,
            avatar_url=avatar_url,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


# 全局实例
auth_service = AuthService()
