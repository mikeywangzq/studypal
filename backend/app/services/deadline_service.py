"""
Deadline service for managing assignment and exam deadlines
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from datetime import datetime, timedelta
import uuid

from ..models.deadline import Deadline
from ..schemas.deadline import DeadlineCreate, DeadlineUpdate


class DeadlineService:
    """Service for deadline management"""

    @staticmethod
    def create_deadline(
        db: Session,
        deadline_create: DeadlineCreate,
        user_id: Optional[str] = None
    ) -> Deadline:
        """
        Create a new deadline

        Args:
            db: Database session
            deadline_create: Deadline creation data
            user_id: User ID

        Returns:
            Created deadline
        """
        deadline = Deadline(
            id=uuid.uuid4(),
            user_id=UUID(user_id) if user_id else None,
            title=deadline_create.title,
            course=deadline_create.course,
            description=deadline_create.description,
            due_date=deadline_create.due_date,
            priority=deadline_create.priority,
            status="pending",
            reminder_sent=False
        )
        db.add(deadline)
        db.commit()
        db.refresh(deadline)
        return deadline

    @staticmethod
    def get_deadline(
        db: Session,
        deadline_id: UUID,
        user_id: Optional[str] = None
    ) -> Optional[Deadline]:
        """Get a deadline by ID"""
        query = db.query(Deadline).filter(Deadline.id == deadline_id)

        if user_id:
            query = query.filter(Deadline.user_id == UUID(user_id))

        return query.first()

    @staticmethod
    def get_deadlines(
        db: Session,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        priority: Optional[str] = None,
        course: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Deadline], int]:
        """
        Get deadlines with filters

        Returns:
            Tuple of (deadlines, total_count)
        """
        query = db.query(Deadline)

        # User filter
        if user_id:
            query = query.filter(Deadline.user_id == UUID(user_id))

        # Status filter
        if status:
            query = query.filter(Deadline.status == status)

        # Date range filter
        if from_date:
            query = query.filter(Deadline.due_date >= from_date)
        if to_date:
            query = query.filter(Deadline.due_date <= to_date)

        # Priority filter
        if priority:
            query = query.filter(Deadline.priority == priority)

        # Course filter
        if course:
            query = query.filter(Deadline.course == course)

        total = query.count()

        # Order by due_date (earliest first)
        deadlines = query.order_by(
            Deadline.due_date.asc()
        ).offset(skip).limit(limit).all()

        return deadlines, total

    @staticmethod
    def get_upcoming_deadlines(
        db: Session,
        user_id: Optional[str] = None,
        days: int = 7
    ) -> List[Deadline]:
        """
        Get upcoming deadlines within specified days

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look ahead

        Returns:
            List of upcoming deadlines
        """
        now = datetime.now()
        future = now + timedelta(days=days)

        query = db.query(Deadline).filter(
            and_(
                Deadline.due_date >= now,
                Deadline.due_date <= future,
                Deadline.status == "pending"
            )
        )

        if user_id:
            query = query.filter(Deadline.user_id == UUID(user_id))

        return query.order_by(Deadline.due_date.asc()).all()

    @staticmethod
    def get_overdue_deadlines(
        db: Session,
        user_id: Optional[str] = None
    ) -> List[Deadline]:
        """
        Get overdue deadlines

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of overdue deadlines
        """
        now = datetime.now()

        query = db.query(Deadline).filter(
            and_(
                Deadline.due_date < now,
                Deadline.status == "pending"
            )
        )

        if user_id:
            query = query.filter(Deadline.user_id == UUID(user_id))

        return query.order_by(Deadline.due_date.desc()).all()

    @staticmethod
    def update_deadline(
        db: Session,
        deadline_id: UUID,
        deadline_update: DeadlineUpdate,
        user_id: Optional[str] = None
    ) -> Optional[Deadline]:
        """Update a deadline"""
        query = db.query(Deadline).filter(Deadline.id == deadline_id)

        if user_id:
            query = query.filter(Deadline.user_id == UUID(user_id))

        deadline = query.first()
        if not deadline:
            return None

        update_data = deadline_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(deadline, key, value)

        db.commit()
        db.refresh(deadline)
        return deadline

    @staticmethod
    def complete_deadline(
        db: Session,
        deadline_id: UUID,
        user_id: Optional[str] = None
    ) -> Optional[Deadline]:
        """Mark a deadline as completed"""
        query = db.query(Deadline).filter(Deadline.id == deadline_id)

        if user_id:
            query = query.filter(Deadline.user_id == UUID(user_id))

        deadline = query.first()
        if not deadline:
            return None

        deadline.status = "completed"
        db.commit()
        db.refresh(deadline)
        return deadline

    @staticmethod
    def delete_deadline(
        db: Session,
        deadline_id: UUID,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete a deadline"""
        query = db.query(Deadline).filter(Deadline.id == deadline_id)

        if user_id:
            query = query.filter(Deadline.user_id == UUID(user_id))

        deadline = query.first()
        if not deadline:
            return False

        db.delete(deadline)
        db.commit()
        return True

    @staticmethod
    def get_deadlines_needing_reminder(
        db: Session,
        days_ahead: int = 3
    ) -> List[Deadline]:
        """
        Get deadlines that need reminders

        Args:
            db: Database session
            days_ahead: Send reminder if deadline is within this many days

        Returns:
            List of deadlines needing reminders
        """
        now = datetime.now()
        reminder_threshold = now + timedelta(days=days_ahead)

        return db.query(Deadline).filter(
            and_(
                Deadline.due_date <= reminder_threshold,
                Deadline.due_date >= now,
                Deadline.status == "pending",
                Deadline.reminder_sent == False
            )
        ).all()

    @staticmethod
    def mark_reminder_sent(
        db: Session,
        deadline_id: UUID
    ) -> bool:
        """Mark that a reminder has been sent for a deadline"""
        deadline = db.query(Deadline).filter(Deadline.id == deadline_id).first()
        if not deadline:
            return False

        deadline.reminder_sent = True
        db.commit()
        return True

    @staticmethod
    def get_statistics(
        db: Session,
        user_id: Optional[str] = None
    ) -> dict:
        """
        Get deadline statistics

        Returns:
            Dictionary with statistics
        """
        query = db.query(Deadline)
        if user_id:
            query = query.filter(Deadline.user_id == UUID(user_id))

        total = query.count()
        pending = query.filter(Deadline.status == "pending").count()
        completed = query.filter(Deadline.status == "completed").count()

        now = datetime.now()
        overdue = query.filter(
            and_(
                Deadline.due_date < now,
                Deadline.status == "pending"
            )
        ).count()

        upcoming = query.filter(
            and_(
                Deadline.due_date >= now,
                Deadline.due_date <= now + timedelta(days=7),
                Deadline.status == "pending"
            )
        ).count()

        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "overdue": overdue,
            "upcoming_7days": upcoming
        }


# Global instance
deadline_service = DeadlineService()
