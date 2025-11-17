"""
Comment Service - 评论服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
import json

from ..models.note_version import NoteComment
from ..models.note import Note
from ..schemas.collaboration import CommentCreate, CommentUpdate


class CommentService:
    """评论服务"""

    @staticmethod
    def create_comment(
        db: Session,
        note_id: UUID,
        user_id: UUID,
        comment_create: CommentCreate
    ) -> Optional[NoteComment]:
        """
        创建评论

        Args:
            db: 数据库会话
            note_id: 笔记ID
            user_id: 用户ID
            comment_create: 评论创建数据

        Returns:
            创建的评论对象
        """
        # 检查笔记是否存在
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return None

        # 如果是回复，检查父评论是否存在
        if comment_create.parent_id:
            parent = db.query(NoteComment).filter(
                NoteComment.id == comment_create.parent_id,
                NoteComment.note_id == note_id
            ).first()
            if not parent:
                return None

        # 创建评论
        comment = NoteComment(
            note_id=note_id,
            user_id=user_id,
            content=comment_create.content,
            parent_id=comment_create.parent_id,
            mentions=json.dumps([str(uid) for uid in comment_create.mentions]) if comment_create.mentions else None,
            is_edited=False
        )

        db.add(comment)
        db.commit()
        db.refresh(comment)

        return comment

    @staticmethod
    def get_note_comments(
        db: Session,
        note_id: UUID,
        include_replies: bool = True
    ) -> List[NoteComment]:
        """
        获取笔记的所有评论

        Args:
            db: 数据库会话
            note_id: 笔记ID
            include_replies: 是否包含回复

        Returns:
            评论列表
        """
        if include_replies:
            # 返回所有评论
            return db.query(NoteComment).filter(
                NoteComment.note_id == note_id
            ).order_by(NoteComment.created_at.asc()).all()
        else:
            # 只返回顶级评论（不包含回复）
            return db.query(NoteComment).filter(
                NoteComment.note_id == note_id,
                NoteComment.parent_id == None
            ).order_by(NoteComment.created_at.asc()).all()

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
        更新评论

        Args:
            db: 数据库会话
            comment_id: 评论ID
            user_id: 用户ID
            comment_update: 更新数据

        Returns:
            更新后的评论对象
        """
        comment = db.query(NoteComment).filter(NoteComment.id == comment_id).first()

        if not comment or comment.user_id != user_id:
            return None

        comment.content = comment_update.content
        comment.is_edited = True

        db.commit()
        db.refresh(comment)

        return comment

    @staticmethod
    def delete_comment(
        db: Session,
        comment_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        删除评论

        Args:
            db: 数据库会话
            comment_id: 评论ID
            user_id: 用户ID

        Returns:
            是否成功
        """
        comment = db.query(NoteComment).filter(NoteComment.id == comment_id).first()

        if not comment or comment.user_id != user_id:
            return False

        # 删除评论及其所有回复（级联删除）
        db.delete(comment)
        db.commit()

        return True

    @staticmethod
    def get_comment_replies(
        db: Session,
        comment_id: UUID
    ) -> List[NoteComment]:
        """
        获取评论的所有回复

        Args:
            db: 数据库会话
            comment_id: 评论ID

        Returns:
            回复列表
        """
        return db.query(NoteComment).filter(
            NoteComment.parent_id == comment_id
        ).order_by(NoteComment.created_at.asc()).all()

    @staticmethod
    def get_user_comments(
        db: Session,
        user_id: UUID,
        limit: int = 50
    ) -> List[NoteComment]:
        """
        获取用户的所有评论

        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回数量限制

        Returns:
            评论列表
        """
        return db.query(NoteComment).filter(
            NoteComment.user_id == user_id
        ).order_by(NoteComment.created_at.desc()).limit(limit).all()


# 全局实例
comment_service = CommentService()
