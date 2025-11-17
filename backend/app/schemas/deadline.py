"""
Pydantic schemas for Deadline endpoints
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class DeadlineCreate(BaseModel):
    """Schema for creating a deadline"""

    title: str
    course: Optional[str] = None
    description: Optional[str] = None
    due_date: datetime
    priority: str = "medium"  # low, medium, high


class DeadlineUpdate(BaseModel):
    """Schema for updating a deadline"""

    title: Optional[str] = None
    course: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class DeadlineResponse(BaseModel):
    """Schema for deadline response"""

    id: UUID
    user_id: Optional[UUID] = None
    title: str
    course: Optional[str] = None
    description: Optional[str] = None
    due_date: datetime
    priority: str
    status: str
    reminder_sent: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeadlineListResponse(BaseModel):
    """Schema for deadline list response"""

    deadlines: list[DeadlineResponse]
    total: int
