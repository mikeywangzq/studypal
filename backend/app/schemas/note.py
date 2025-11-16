"""
Pydantic schemas for Note endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class NoteCreate(BaseModel):
    """Schema for creating a note"""

    title: str
    file_type: str
    content: str
    category: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    """Schema for updating a note"""

    title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    content: Optional[str] = None


class NoteResponse(BaseModel):
    """Schema for note response"""

    id: UUID
    user_id: Optional[UUID] = None
    title: str
    file_type: str
    file_path: str
    content: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Schema for note list response"""

    notes: List[NoteResponse]
    total: int
    page: int
    limit: int
