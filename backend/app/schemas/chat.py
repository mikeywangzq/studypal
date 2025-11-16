"""
Pydantic schemas for Chat endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class SourceReference(BaseModel):
    """Schema for source reference in chat response"""

    note_id: UUID
    title: str
    content_snippet: str
    relevance_score: float


class ChatRequest(BaseModel):
    """Schema for chat request"""

    question: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    """Schema for chat response"""

    answer: str
    sources: List[SourceReference]
    conversation_id: UUID


class MessageResponse(BaseModel):
    """Schema for message response"""

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation response"""

    id: UUID
    user_id: Optional[UUID] = None
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: Optional[List[MessageResponse]] = None

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Schema for conversation list response"""

    conversations: List[ConversationResponse]
    total: int
