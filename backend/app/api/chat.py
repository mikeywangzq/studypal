"""
Chat API endpoints for RAG-based Q&A
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationListResponse,
    MessageResponse
)
from ..services.rag_service import rag_service

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question and get an AI-powered answer based on your notes

    - **question**: Your question (1-2000 characters)
    - **conversation_id**: Optional conversation ID to continue existing conversation

    The system will:
    1. Search your notes for relevant content
    2. Use the context to generate an intelligent answer
    3. Return the answer with source references
    """
    try:
        response = await rag_service.answer_question(
            db=db,
            chat_request=chat_request,
            user_id=None  # TODO: Get from auth
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in ask_question: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer. Please try again."
        )


@router.get("/conversations", response_model=ConversationListResponse)
def get_conversations(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get list of conversations

    - **page**: Page number (starts from 1)
    - **limit**: Number of items per page
    """
    skip = (page - 1) * limit

    conversations, total = rag_service.get_conversations(
        db=db,
        user_id=None,  # TODO: Get from auth
        skip=skip,
        limit=limit
    )

    return ConversationListResponse(
        conversations=[
            ConversationResponse.model_validate(conv)
            for conv in conversations
        ],
        total=total
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation with all messages

    - **conversation_id**: ID of the conversation
    """
    conversation = rag_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=None  # TODO: Get from auth
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Load messages
    from ..models.conversation import Message
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()

    response = ConversationResponse.model_validate(conversation)
    response.messages = [
        MessageResponse.model_validate(msg)
        for msg in messages
    ]

    return response


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages

    - **conversation_id**: ID of the conversation to delete
    """
    success = rag_service.delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=None  # TODO: Get from auth
    )

    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted successfully"}


@router.put("/conversations/{conversation_id}/title")
def update_conversation_title(
    conversation_id: UUID,
    title: str = Query(..., min_length=1, max_length=200),
    db: Session = Depends(get_db)
):
    """
    Update conversation title

    - **conversation_id**: ID of the conversation
    - **title**: New title
    """
    from ..models.conversation import Conversation

    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.title = title
    db.commit()
    db.refresh(conversation)

    return ConversationResponse.model_validate(conversation)
