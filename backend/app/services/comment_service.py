"""
Comment Service - 评论服务

提供评论管理功能：
- 创建评论和回复
- 查询评论列表
- 更新和删除评论
- @提及用户功能
- 嵌套回复支持
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
import json
import logging

from ..models.note_version import NoteComment
from ..models.note import Note
from ..schemas.collaboration import CommentCreate, CommentUpdate

# 配置日志
logger = logging.getLogger(__name__)


class CommentService:
    """
    评论服务类

    功能特点：
    1. 支持两层评论结构（顶层评论 + 回复）
    2. 支持@提及多个用户
    3. 记录评论编辑状态
    4. 级联删除（删除父评论时自动删除所有子回复）
    """

    @staticmethod
    def create_comment(
        db: Session,
        note_id: UUID,
        user_id: UUID,
        comment_create: CommentCreate
    ) -> Optional[NoteComment]:
        """
        创建评论或回复

        功能说明：
        - 如果parent_id为None，创建顶层评论
        - 如果parent_id有值，创建回复
        - 支持@提及多个用户（存储为JSON数组）

        校验：
        1. 检查笔记是否存在
        2. 如果是回复，检查父评论是否存在且属于同一笔记

        Args:
            db: 数据库会话
            note_id: 笔记ID
            user_id: 评论者用户ID
            comment_create: 评论创建数据（包含content、parent_id、mentions）

        Returns:
            创建的评论对象，如果笔记或父评论不存在则返回None
        """
        # 检查笔记是否存在
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            logger.warning(f"笔记不存在，无法创建评论: note_id={note_id}")
            return None

        # 如果是回复，检查父评论是否存在且属于同一笔记
        if comment_create.parent_id:
            parent = db.query(NoteComment).filter(
                NoteComment.id == comment_create.parent_id,
                NoteComment.note_id == note_id  # 确保父评论属于同一笔记
            ).first()
            if not parent:
                logger.warning(f"父评论不存在或不属于此笔记: parent_id={comment_create.parent_id}, note_id={note_id}")
                return None

        try:
            # 创建评论
            # 将mentions中的UUID列表转换为JSON字符串存储
            mentions_json = None
            if comment_create.mentions:
                try:
                    mentions_json = json.dumps([str(uid) for uid in comment_create.mentions], ensure_ascii=False)
                except Exception as e:
                    logger.error(f"序列化mentions失败: {e}")
                    # 继续创建评论，但不保存mentions
                    mentions_json = None

            comment = NoteComment(
                note_id=note_id,
                user_id=user_id,
                content=comment_create.content,
                parent_id=comment_create.parent_id,
                mentions=mentions_json,
                is_edited=False
            )

            db.add(comment)
            db.commit()
            db.refresh(comment)

            logger.info(f"成功创建评论: comment_id={comment.id}, note_id={note_id}, is_reply={comment.parent_id is not None}")
            return comment

        except Exception as e:
            logger.error(f"创建评论失败: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_note_comments(
        db: Session,
        note_id: UUID,
        include_replies: bool = True
    ) -> List[NoteComment]:
        """
        获取笔记的所有评论

        两种模式：
        1. include_replies=True：返回所有评论（包括顶层评论和回复）
        2. include_replies=False：只返回顶层评论（parent_id为NULL）

        排序：按创建时间升序（最早的在前）

        Args:
            db: 数据库会话
            note_id: 笔记ID
            include_replies: 是否包含回复，默认为True

        Returns:
            评论列表（按创建时间升序排列）
        """
        try:
            if include_replies:
                # 返回所有评论（顶层评论 + 所有回复）
                comments = db.query(NoteComment).filter(
                    NoteComment.note_id == note_id
                ).order_by(NoteComment.created_at.asc()).all()

                logger.info(f"获取笔记评论成功: note_id={note_id}, 数量={len(comments)} (包含回复)")
                return comments
            else:
                # 只返回顶级评论（parent_id为NULL）
                comments = db.query(NoteComment).filter(
                    NoteComment.note_id == note_id,
                    NoteComment.parent_id == None
                ).order_by(NoteComment.created_at.asc()).all()

                logger.info(f"获取笔记顶层评论成功: note_id={note_id}, 数量={len(comments)}")
                return comments

        except Exception as e:
            logger.error(f"获取评论失败: {e}")
            return []

    @staticmethod
    def get_comment_by_id(
        db: Session,
        comment_id: UUID
    ) -> Optional[NoteComment]:
        """
        通过ID获取评论

        Args:
            db: 数据库会话
            comment_id: 评论ID

        Returns:
            评论对象或None
        """
        return db.query(NoteComment).filter(NoteComment.id == comment_id).first()

    @staticmethod
    def update_comment(
        db: Session,
        comment_id: UUID,
        user_id: UUID,
        comment_update: CommentUpdate
    ) -> Optional[NoteComment]:
        """
        更新评论内容

        权限检查：
        - 只有评论的作者可以更新自己的评论
        - user_id必须与评论的user_id匹配

        更新内容：
        - content：评论文本
        - is_edited：自动设置为True，标记评论已被编辑

        Args:
            db: 数据库会话
            comment_id: 评论ID
            user_id: 当前用户ID（必须是评论作者）
            comment_update: 更新数据（包含新的content）

        Returns:
            更新后的评论对象，如果评论不存在或无权限则返回None
        """
        try:
            comment = db.query(NoteComment).filter(NoteComment.id == comment_id).first()

            # 检查评论是否存在
            if not comment:
                logger.warning(f"评论不存在: comment_id={comment_id}")
                return None

            # 检查权限（只有作者可以更新）
            if comment.user_id != user_id:
                logger.warning(f"用户无权限更新评论: comment_id={comment_id}, user_id={user_id}, owner_id={comment.user_id}")
                return None

            # 更新评论内容
            comment.content = comment_update.content
            comment.is_edited = True  # 标记为已编辑

            db.commit()
            db.refresh(comment)

            logger.info(f"成功更新评论: comment_id={comment_id}")
            return comment

        except Exception as e:
            logger.error(f"更新评论失败: {e}")
            db.rollback()
            return None

    @staticmethod
    def delete_comment(
        db: Session,
        comment_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        删除评论

        权限检查：
        - 只有评论的作者可以删除自己的评论
        - user_id必须与评论的user_id匹配

        级联删除：
        - 删除评论时会自动删除所有子回复
        - 由数据库外键约束（ondelete="CASCADE"）自动处理

        Args:
            db: 数据库会话
            comment_id: 评论ID
            user_id: 当前用户ID（必须是评论作者）

        Returns:
            是否成功，如果评论不存在或无权限则返回False
        """
        try:
            comment = db.query(NoteComment).filter(NoteComment.id == comment_id).first()

            # 检查评论是否存在
            if not comment:
                logger.warning(f"评论不存在: comment_id={comment_id}")
                return False

            # 检查权限（只有作者可以删除）
            if comment.user_id != user_id:
                logger.warning(f"用户无权限删除评论: comment_id={comment_id}, user_id={user_id}, owner_id={comment.user_id}")
                return False

            # 删除评论（会级联删除所有子回复）
            db.delete(comment)
            db.commit()

            logger.info(f"成功删除评论: comment_id={comment_id}")
            return True

        except Exception as e:
            logger.error(f"删除评论失败: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_comment_replies(
        db: Session,
        comment_id: UUID
    ) -> List[NoteComment]:
        """
        获取评论的所有回复

        用于构建评论树结构：
        1. 先查询所有顶层评论（parent_id为NULL）
        2. 对每个顶层评论，调用此方法获取其回复

        排序：按创建时间升序（最早的回复在前）

        Args:
            db: 数据库会话
            comment_id: 父评论ID

        Returns:
            回复列表（按创建时间升序排列）
        """
        try:
            replies = db.query(NoteComment).filter(
                NoteComment.parent_id == comment_id
            ).order_by(NoteComment.created_at.asc()).all()

            logger.info(f"获取评论回复成功: comment_id={comment_id}, 回复数={len(replies)}")
            return replies

        except Exception as e:
            logger.error(f"获取评论回复失败: {e}")
            return []

    @staticmethod
    def get_user_comments(
        db: Session,
        user_id: UUID,
        limit: int = 50
    ) -> List[NoteComment]:
        """
        获取用户的所有评论

        用途：
        - 用户个人中心显示评论历史
        - 统计用户评论数量
        - 查看用户最近的评论

        排序：按创建时间降序（最新的评论在前）
        限制：默认返回最近50条

        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回数量限制，默认50

        Returns:
            评论列表（按创建时间降序排列）
        """
        try:
            comments = db.query(NoteComment).filter(
                NoteComment.user_id == user_id
            ).order_by(NoteComment.created_at.desc()).limit(limit).all()

            logger.info(f"获取用户评论成功: user_id={user_id}, 数量={len(comments)}")
            return comments

        except Exception as e:
            logger.error(f"获取用户评论失败: {e}")
            return []


# 全局实例
comment_service = CommentService()
