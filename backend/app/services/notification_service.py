"""
Notification Service - 通知服务

提供通知管理功能：
- 创建各类通知（分享、评论、提及、权限变更）
- 查询用户通知列表
- 标记已读/未读
- 删除通知
- 统计通知数据
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from datetime import datetime
import logging

from ..models.note_version import Notification
from ..schemas.collaboration import NotificationCreate

# 配置日志
logger = logging.getLogger(__name__)


class NotificationService:
    """
    通知服务类

    支持的通知类型：
    1. share - 笔记分享通知（有人分享笔记给用户）
    2. comment - 评论通知（用户的笔记收到新评论）
    3. mention - 提及通知（用户在评论中被@提及）
    4. permission - 权限变更通知（用户获得或失去笔记权限）

    设计特点：
    - 通过resource_type和resource_id关联相关资源
    - 通过actor_id记录通知发起者
    - 支持已读/未读状态管理
    - 提供按类型统计功能
    """

    @staticmethod
    def create_notification(
        db: Session,
        notification_create: NotificationCreate
    ) -> Optional[Notification]:
        """
        创建通知（通用方法）

        通知字段说明：
        - user_id: 接收通知的用户（必填）
        - type: 通知类型（share/comment/mention/permission）
        - title: 通知标题
        - message: 通知详细消息
        - resource_type: 关联资源类型（note/comment/share）
        - resource_id: 关联资源ID
        - actor_id: 触发通知的用户ID

        注意：
        - 新创建的通知默认is_read=False（未读）
        - read_at初始为NULL
        - 自动去重：如果已存在相同的未读通知，不创建新通知

        Args:
            db: 数据库会话
            notification_create: 通知创建数据

        Returns:
            创建的通知对象，失败则返回None
        """
        try:
            # 去重检查：检查是否已存在相同的未读通知
            # 相同通知定义：相同用户、相同类型、相同资源、相同actor
            existing = db.query(Notification).filter(
                Notification.user_id == notification_create.user_id,
                Notification.type == notification_create.type,
                Notification.resource_id == notification_create.resource_id,
                Notification.actor_id == notification_create.actor_id,
                Notification.is_read == False  # 只检查未读通知
            ).first()

            if existing:
                logger.info(f"通知已存在，跳过创建: type={notification_create.type}, user_id={notification_create.user_id}, resource_id={notification_create.resource_id}")
                return existing  # 返回已存在的通知

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

            logger.info(f"成功创建通知: type={notification.type}, user_id={notification.user_id}")
            return notification

        except Exception as e:
            logger.error(f"创建通知失败: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: UUID,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """
        获取用户的通知列表

        查询模式：
        1. unread_only=False：返回所有通知（已读+未读）
        2. unread_only=True：只返回未读通知

        排序：按创建时间降序（最新的通知在前）
        限制：默认返回最近50条

        Args:
            db: 数据库会话
            user_id: 用户ID
            unread_only: 是否只获取未读通知，默认False
            limit: 返回数量限制，默认50

        Returns:
            通知列表（按创建时间降序排列）
        """
        try:
            query = db.query(Notification).filter(Notification.user_id == user_id)

            # 如果只要未读通知，添加过滤条件
            if unread_only:
                query = query.filter(Notification.is_read == False)

            notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()

            logger.info(f"获取用户通知成功: user_id={user_id}, 数量={len(notifications)}, 仅未读={unread_only}")
            return notifications

        except Exception as e:
            logger.error(f"获取用户通知失败: {e}")
            return []

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        标记通知为已读

        权限检查：
        - 只能标记自己的通知为已读
        - user_id必须与通知的user_id匹配

        更新内容：
        - is_read设置为True
        - read_at设置为当前UTC时间

        Args:
            db: 数据库会话
            notification_id: 通知ID
            user_id: 用户ID

        Returns:
            是否成功，如果通知不存在或不属于该用户则返回False
        """
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id  # 确保通知属于该用户
            ).first()

            if not notification:
                logger.warning(f"通知不存在或无权限: notification_id={notification_id}, user_id={user_id}")
                return False

            # 如果已经是已读状态，直接返回成功
            if notification.is_read:
                logger.info(f"通知已是已读状态: notification_id={notification_id}")
                return True

            # 标记为已读
            notification.is_read = True
            notification.read_at = datetime.utcnow()

            db.commit()

            logger.info(f"成功标记通知为已读: notification_id={notification_id}")
            return True

        except Exception as e:
            logger.error(f"标记通知已读失败: {e}")
            db.rollback()
            return False

    @staticmethod
    def mark_all_as_read(
        db: Session,
        user_id: UUID
    ) -> int:
        """
        标记所有通知为已读

        批量操作：
        - 查询该用户的所有未读通知
        - 将它们全部标记为已读
        - 设置read_at为当前UTC时间

        性能优化建议：
        - 对于大量通知，可以使用批量update代替逐个更新
        - 当前实现简单易懂，适合通知数量不多的场景

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            更新的通知数量
        """
        try:
            # 查询所有未读通知
            notifications = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).all()

            count = len(notifications)

            if count == 0:
                logger.info(f"用户没有未读通知: user_id={user_id}")
                return 0

            # 批量标记为已读
            current_time = datetime.utcnow()
            for notification in notifications:
                notification.is_read = True
                notification.read_at = current_time

            db.commit()

            logger.info(f"成功标记所有通知为已读: user_id={user_id}, 数量={count}")
            return count

        except Exception as e:
            logger.error(f"批量标记通知已读失败: {e}")
            db.rollback()
            return 0

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        删除通知

        权限检查：
        - 只能删除自己的通知
        - user_id必须与通知的user_id匹配

        注意：
        - 删除是永久性的，无法恢复
        - 建议在删除前确认用户意图

        Args:
            db: 数据库会话
            notification_id: 通知ID
            user_id: 用户ID

        Returns:
            是否成功，如果通知不存在或不属于该用户则返回False
        """
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id  # 确保通知属于该用户
            ).first()

            if not notification:
                logger.warning(f"通知不存在或无权限: notification_id={notification_id}, user_id={user_id}")
                return False

            db.delete(notification)
            db.commit()

            logger.info(f"成功删除通知: notification_id={notification_id}")
            return True

        except Exception as e:
            logger.error(f"删除通知失败: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_notification_stats(
        db: Session,
        user_id: UUID
    ) -> dict:
        """
        获取通知统计信息

        返回数据：
        - total: 总通知数
        - unread: 未读通知数
        - by_type: 按类型统计的字典
          {
              'share': 5,
              'comment': 10,
              'mention': 3,
              'permission': 2
          }

        用途：
        - 在通知中心显示统计数据
        - 用户个人中心展示通知概览
        - 生成通知活动报告

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            统计字典，包含total、unread、by_type
        """
        try:
            # 查询用户的所有通知
            all_notifications = db.query(Notification).filter(
                Notification.user_id == user_id
            ).all()

            total = len(all_notifications)
            unread = sum(1 for n in all_notifications if not n.is_read)

            # 按类型统计
            by_type = {}
            for notification in all_notifications:
                notification_type = notification.type
                by_type[notification_type] = by_type.get(notification_type, 0) + 1

            stats = {
                'total': total,
                'unread': unread,
                'by_type': by_type
            }

            logger.info(f"获取通知统计成功: user_id={user_id}, total={total}, unread={unread}")
            return stats

        except Exception as e:
            logger.error(f"获取通知统计失败: {e}")
            return {
                'total': 0,
                'unread': 0,
                'by_type': {}
            }

    # ========== 特定类型通知创建辅助方法 ==========

    @staticmethod
    def notify_share(
        db: Session,
        user_id: UUID,
        note_title: str,
        sharer_id: UUID,
        note_id: UUID
    ) -> Optional[Notification]:
        """
        创建笔记分享通知

        触发场景：
        - 用户A将笔记分享给用户B
        - 系统自动创建通知发送给用户B

        通知内容：
        - type: 'share'
        - title: '新的笔记分享'
        - message: '有人分享了笔记《{笔记标题}》给您'
        - actor: 分享者

        Args:
            db: 数据库会话
            user_id: 接收通知的用户ID（被分享者）
            note_title: 笔记标题
            sharer_id: 分享者用户ID
            note_id: 笔记ID

        Returns:
            创建的通知对象，失败则返回None
        """
        logger.info(f"创建分享通知: note={note_title}, from={sharer_id}, to={user_id}")
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
    ) -> Optional[Notification]:
        """
        创建评论通知

        触发场景：
        - 用户A在用户B的笔记下发表评论
        - 系统自动创建通知发送给笔记所有者B

        通知内容：
        - type: 'comment'
        - title: '新的评论'
        - message: '您的笔记《{笔记标题}》有新评论'
        - actor: 评论者

        Args:
            db: 数据库会话
            user_id: 接收通知的用户ID（笔记所有者）
            note_title: 笔记标题
            commenter_id: 评论者用户ID
            note_id: 笔记ID
            comment_id: 评论ID

        Returns:
            创建的通知对象，失败则返回None
        """
        logger.info(f"创建评论通知: note={note_title}, commenter={commenter_id}, owner={user_id}")
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
    ) -> Optional[Notification]:
        """
        创建@提及通知

        触发场景：
        - 用户A在评论中@提及了用户B
        - 系统自动创建通知发送给被提及者B

        通知内容：
        - type: 'mention'
        - title: '有人提到了您'
        - message: '有人在《{笔记标题}》的评论中提到了您'
        - actor: 提及者

        Args:
            db: 数据库会话
            user_id: 接收通知的用户ID（被提及者）
            note_title: 笔记标题
            mentioner_id: 提及者用户ID
            comment_id: 评论ID

        Returns:
            创建的通知对象，失败则返回None
        """
        logger.info(f"创建提及通知: note={note_title}, mentioner={mentioner_id}, mentioned={user_id}")
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
    ) -> Optional[Notification]:
        """
        创建权限变更通知

        触发场景：
        - 用户A修改了用户B对某笔记的权限
        - 系统自动创建通知发送给用户B

        权限级别：
        - 'view': 查看权限
        - 'edit': 编辑权限
        - 'owner': 所有者权限

        通知内容：
        - type: 'permission'
        - title: '笔记权限变更'
        - message: '您获得了《{笔记标题}》的{权限级别}权限'
        - actor: 授权者

        Args:
            db: 数据库会话
            user_id: 接收通知的用户ID（被授权者）
            note_title: 笔记标题
            granter_id: 授权者用户ID
            note_id: 笔记ID
            permission_level: 权限级别（view/edit/owner）

        Returns:
            创建的通知对象，失败则返回None
        """
        logger.info(f"创建权限通知: note={note_title}, granter={granter_id}, grantee={user_id}, level={permission_level}")
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
