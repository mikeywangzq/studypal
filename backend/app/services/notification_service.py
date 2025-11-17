"""
Notification Service - 通知服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from datetime import datetime

from ..models.note_version import Notification
from ..schemas.collaboration import NotificationCreate


class NotificationService:
    """通知服务"""

    @staticmethod
    def create_notification(
        db: Session,
        notification_create: NotificationCreate
    ) -> Notification:
        """
        创建通知

        Args:
            db: 数据库会话
            notification_create: 通知创建数据

        Returns:
            创建的通知对象
        """
        notification = Notification(
            user_id=notification_create.user_id,
            type=notification_create.type,
            title=notification_create.title,
            message=notification_create.message,
            resource_type=notification_create.resource_type,
            resource_id=notification_create.resource_id,
            actor_id=notification_create.actor_id,
            is_read=False
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """
        获取用户的通知

        Args:
            db: 数据库会话
            user_id: 用户ID
            unread_only: 是否只获取未读通知
            limit: 返回数量限制

        Returns:
            通知列表
        """
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        标记通知为已读

        Args:
            db: 数据库会话
            notification_id: 通知ID
            user_id: 用户ID

        Returns:
            是否成功
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        db.commit()

        return True

    @staticmethod
    def mark_all_as_read(
        db: Session,
        user_id: UUID
    ) -> int:
        """
        标记所有通知为已读

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            更新的通知数量
        """
        notifications = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).all()

        count = len(notifications)

        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()

        db.commit()

        return count

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        删除通知

        Args:
            db: 数据库会话
            notification_id: 通知ID
            user_id: 用户ID

        Returns:
            是否成功
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            return False

        db.delete(notification)
        db.commit()

        return True

    @staticmethod
    def get_notification_stats(
        db: Session,
        user_id: UUID
    ) -> dict:
        """
        获取通知统计

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            统计字典
        """
        all_notifications = db.query(Notification).filter(
            Notification.user_id == user_id
        ).all()

        total = len(all_notifications)
        unread = sum(1 for n in all_notifications if not n.is_read)

        # 按类型统计
        by_type = {}
        for notification in all_notifications:
            by_type[notification.type] = by_type.get(notification.type, 0) + 1

        return {
            'total': total,
            'unread': unread,
            'by_type': by_type
        }

    # ========== 特定类型通知创建辅助方法 ==========

    @staticmethod
    def notify_share(
        db: Session,
        user_id: UUID,
        note_title: str,
        sharer_id: UUID,
        note_id: UUID
    ):
        """创建分享通知"""
        return NotificationService.create_notification(db, NotificationCreate(
            user_id=user_id,
            type='share',
            title='新的笔记分享',
            message=f'有人分享了笔记《{note_title}》给您',
            resource_type='note',
            resource_id=note_id,
            actor_id=sharer_id
        ))

    @staticmethod
    def notify_comment(
        db: Session,
        user_id: UUID,
        note_title: str,
        commenter_id: UUID,
        note_id: UUID,
        comment_id: UUID
    ):
        """创建评论通知"""
        return NotificationService.create_notification(db, NotificationCreate(
            user_id=user_id,
            type='comment',
            title='新的评论',
            message=f'您的笔记《{note_title}》有新评论',
            resource_type='comment',
            resource_id=comment_id,
            actor_id=commenter_id
        ))

    @staticmethod
    def notify_mention(
        db: Session,
        user_id: UUID,
        note_title: str,
        mentioner_id: UUID,
        comment_id: UUID
    ):
        """创建提及通知"""
        return NotificationService.create_notification(db, NotificationCreate(
            user_id=user_id,
            type='mention',
            title='有人提到了您',
            message=f'有人在《{note_title}》的评论中提到了您',
            resource_type='comment',
            resource_id=comment_id,
            actor_id=mentioner_id
        ))

    @staticmethod
    def notify_permission(
        db: Session,
        user_id: UUID,
        note_title: str,
        granter_id: UUID,
        note_id: UUID,
        permission_level: str
    ):
        """创建权限变更通知"""
        return NotificationService.create_notification(db, NotificationCreate(
            user_id=user_id,
            type='permission',
            title='笔记权限变更',
            message=f'您获得了《{note_title}》的{permission_level}权限',
            resource_type='note',
            resource_id=note_id,
            actor_id=granter_id
        ))


# 全局实例
notification_service = NotificationService()
