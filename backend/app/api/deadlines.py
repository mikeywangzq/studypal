"""
Deadlines API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..database import get_db
from ..schemas.deadline import (
    DeadlineCreate,
    DeadlineUpdate,
    DeadlineResponse,
    DeadlineListResponse
)
from ..services.deadline_service import deadline_service

router = APIRouter()


@router.post("", response_model=DeadlineResponse, status_code=201)
def create_deadline(
    deadline_create: DeadlineCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new deadline

    - **title**: Deadline title (required)
    - **course**: Course name (optional)
    - **description**: Description (optional)
    - **due_date**: Due date and time (required)
    - **priority**: Priority level (low, medium, high)
    """
    # Validate due_date is in the future
    if deadline_create.due_date < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Due date must be in the future"
        )

    deadline = deadline_service.create_deadline(
        db=db,
        deadline_create=deadline_create,
        user_id=None  # TODO: Get from auth
    )

    return DeadlineResponse.model_validate(deadline)


@router.get("", response_model=DeadlineListResponse)
def get_deadlines(
    status: Optional[str] = Query(None, regex="^(pending|completed)$"),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    course: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get list of deadlines with filters

    - **status**: Filter by status (pending, completed)
    - **from_date**: Filter deadlines from this date
    - **to_date**: Filter deadlines until this date
    - **priority**: Filter by priority (low, medium, high)
    - **course**: Filter by course name
    - **page**: Page number
    - **limit**: Items per page
    """
    skip = (page - 1) * limit

    deadlines, total = deadline_service.get_deadlines(
        db=db,
        user_id=None,  # TODO: Get from auth
        status=status,
        from_date=from_date,
        to_date=to_date,
        priority=priority,
        course=course,
        skip=skip,
        limit=limit
    )

    return DeadlineListResponse(
        deadlines=[DeadlineResponse.model_validate(d) for d in deadlines],
        total=total
    )


@router.get("/upcoming", response_model=List[DeadlineResponse])
def get_upcoming_deadlines(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get upcoming deadlines within specified days

    - **days**: Number of days to look ahead (default: 7, max: 30)
    """
    deadlines = deadline_service.get_upcoming_deadlines(
        db=db,
        user_id=None,  # TODO: Get from auth
        days=days
    )

    return [DeadlineResponse.model_validate(d) for d in deadlines]


@router.get("/overdue", response_model=List[DeadlineResponse])
def get_overdue_deadlines(
    db: Session = Depends(get_db)
):
    """
    Get all overdue deadlines
    """
    deadlines = deadline_service.get_overdue_deadlines(
        db=db,
        user_id=None  # TODO: Get from auth
    )

    return [DeadlineResponse.model_validate(d) for d in deadlines]


@router.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db)
):
    """
    Get deadline statistics

    Returns counts for:
    - total: Total deadlines
    - pending: Pending deadlines
    - completed: Completed deadlines
    - overdue: Overdue deadlines
    - upcoming_7days: Due within 7 days
    """
    stats = deadline_service.get_statistics(
        db=db,
        user_id=None  # TODO: Get from auth
    )

    return stats


@router.get("/{deadline_id}", response_model=DeadlineResponse)
def get_deadline(
    deadline_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific deadline by ID
    """
    deadline = deadline_service.get_deadline(
        db=db,
        deadline_id=deadline_id,
        user_id=None  # TODO: Get from auth
    )

    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")

    return DeadlineResponse.model_validate(deadline)


@router.put("/{deadline_id}", response_model=DeadlineResponse)
def update_deadline(
    deadline_id: UUID,
    deadline_update: DeadlineUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a deadline

    Can update any of:
    - title
    - course
    - description
    - due_date
    - priority
    - status
    """
    deadline = deadline_service.update_deadline(
        db=db,
        deadline_id=deadline_id,
        deadline_update=deadline_update,
        user_id=None  # TODO: Get from auth
    )

    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")

    return DeadlineResponse.model_validate(deadline)


@router.patch("/{deadline_id}/complete", response_model=DeadlineResponse)
def complete_deadline(
    deadline_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Mark a deadline as completed
    """
    deadline = deadline_service.complete_deadline(
        db=db,
        deadline_id=deadline_id,
        user_id=None  # TODO: Get from auth
    )

    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")

    return DeadlineResponse.model_validate(deadline)


@router.delete("/{deadline_id}")
def delete_deadline(
    deadline_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a deadline
    """
    success = deadline_service.delete_deadline(
        db=db,
        deadline_id=deadline_id,
        user_id=None  # TODO: Get from auth
    )

    if not success:
        raise HTTPException(status_code=404, detail="Deadline not found")

    return {"message": "Deadline deleted successfully"}
