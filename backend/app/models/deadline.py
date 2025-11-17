"""
Deadline model for DDL management
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..database import Base


class Deadline(Base):
    """Deadline model for managing assignment and exam deadlines"""

    __tablename__ = "deadlines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Nullable for MVP
    title = Column(String, nullable=False)
    course = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    priority = Column(String, default="medium")  # low, medium, high
    status = Column(String, default="pending", index=True)  # pending, completed
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
