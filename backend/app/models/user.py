"""
User model for authentication
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..database import Base


class User(Base):
    """User model for authentication (optional in MVP)"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    # Profile fields
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)

    # Password reset
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'github', etc.
    oauth_id = Column(String(255), nullable=True)  # OAuth provider's user ID

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
