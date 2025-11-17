"""
Export Service - 数据导出服务
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
import json
import csv
from io import StringIO
from datetime import datetime

from ..models.note import Note
from ..models.conversation import Conversation, Message
from ..models.deadline import Deadline


class ExportService:
    """数据导出服务"""

    @staticmethod
    def export_notes_to_json(db: Session, user_id: Optional[UUID] = None) -> str:
        """
        导出笔记为 JSON 格式

        Args:
            db: 数据库会话
            user_id: 用户ID（可选）

        Returns:
            JSON 字符串
        """
        query = db.query(Note)
        if user_id:
            query = query.filter(Note.user_id == user_id)

        notes = query.all()

        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_notes": len(notes),
            "notes": [
                {
                    "id": str(note.id),
                    "title": note.title,
                    "file_type": note.file_type,
                    "content": note.content,
                    "category": note.category,
                    "tags": note.tags,
                    "created_at": note.created_at.isoformat() if note.created_at else None,
                    "updated_at": note.updated_at.isoformat() if note.updated_at else None,
                }
                for note in notes
            ]
        }

        return json.dumps(export_data, ensure_ascii=False, indent=2)

    @staticmethod
    def export_notes_to_markdown(db: Session, user_id: Optional[UUID] = None) -> str:
        """
        导出笔记为 Markdown 格式

        Args:
            db: 数据库会话
            user_id: 用户ID（可选）

        Returns:
            Markdown 字符串
        """
        query = db.query(Note)
        if user_id:
            query = query.filter(Note.user_id == user_id)

        notes = query.order_by(Note.category, Note.created_at).all()

        markdown_content = []
        markdown_content.append("# StudyPal 笔记导出\n")
        markdown_content.append(f"导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        markdown_content.append(f"笔记总数：{len(notes)}\n")
        markdown_content.append("\n---\n\n")

        # 按分类组织
        current_category = None
        for note in notes:
            if note.category != current_category:
                current_category = note.category
                markdown_content.append(f"\n## {current_category or '未分类'}\n\n")

            markdown_content.append(f"### {note.title}\n\n")

            if note.tags:
                tags_str = " ".join([f"`{tag}`" for tag in note.tags])
                markdown_content.append(f"**标签**: {tags_str}\n\n")

            if note.created_at:
                markdown_content.append(
                    f"**创建时间**: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )

            markdown_content.append(note.content)
            markdown_content.append("\n\n---\n\n")

        return "".join(markdown_content)

    @staticmethod
    def export_conversations_to_json(
        db: Session,
        user_id: Optional[UUID] = None
    ) -> str:
        """
        导出对话为 JSON 格式

        Args:
            db: 数据库会话
            user_id: 用户ID（可选）

        Returns:
            JSON 字符串
        """
        query = db.query(Conversation)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)

        conversations = query.all()

        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_conversations": len(conversations),
            "conversations": []
        }

        for conv in conversations:
            messages = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at).all()

            conv_data = {
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "sources": msg.sources,
                        "created_at": msg.created_at.isoformat() if msg.created_at else None,
                    }
                    for msg in messages
                ]
            }
            export_data["conversations"].append(conv_data)

        return json.dumps(export_data, ensure_ascii=False, indent=2)

    @staticmethod
    def export_deadlines_to_json(
        db: Session,
        user_id: Optional[UUID] = None
    ) -> str:
        """
        导出 DDL 为 JSON 格式

        Args:
            db: 数据库会话
            user_id: 用户ID（可选）

        Returns:
            JSON 字符串
        """
        query = db.query(Deadline)
        if user_id:
            query = query.filter(Deadline.user_id == user_id)

        deadlines = query.order_by(Deadline.due_date).all()

        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_deadlines": len(deadlines),
            "deadlines": [
                {
                    "id": str(deadline.id),
                    "title": deadline.title,
                    "course": deadline.course,
                    "description": deadline.description,
                    "due_date": deadline.due_date.isoformat() if deadline.due_date else None,
                    "priority": deadline.priority,
                    "status": deadline.status,
                    "created_at": deadline.created_at.isoformat() if deadline.created_at else None,
                    "completed_at": deadline.completed_at.isoformat() if deadline.completed_at else None,
                }
                for deadline in deadlines
            ]
        }

        return json.dumps(export_data, ensure_ascii=False, indent=2)

    @staticmethod
    def export_deadlines_to_csv(
        db: Session,
        user_id: Optional[UUID] = None
    ) -> str:
        """
        导出 DDL 为 CSV 格式

        Args:
            db: 数据库会话
            user_id: 用户ID（可选）

        Returns:
            CSV 字符串
        """
        query = db.query(Deadline)
        if user_id:
            query = query.filter(Deadline.user_id == user_id)

        deadlines = query.order_by(Deadline.due_date).all()

        output = StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow([
            "标题",
            "课程",
            "描述",
            "截止时间",
            "优先级",
            "状态",
            "创建时间",
            "完成时间"
        ])

        # 写入数据
        for deadline in deadlines:
            writer.writerow([
                deadline.title,
                deadline.course or "",
                deadline.description or "",
                deadline.due_date.strftime('%Y-%m-%d %H:%M:%S') if deadline.due_date else "",
                deadline.priority,
                deadline.status,
                deadline.created_at.strftime('%Y-%m-%d %H:%M:%S') if deadline.created_at else "",
                deadline.completed_at.strftime('%Y-%m-%d %H:%M:%S') if deadline.completed_at else "",
            ])

        return output.getvalue()

    @staticmethod
    def export_all_data(db: Session, user_id: Optional[UUID] = None) -> dict:
        """
        导出所有数据

        Args:
            db: 数据库会话
            user_id: 用户ID（可选）

        Returns:
            包含所有数据的字典
        """
        notes_json = json.loads(ExportService.export_notes_to_json(db, user_id))
        conversations_json = json.loads(ExportService.export_conversations_to_json(db, user_id))
        deadlines_json = json.loads(ExportService.export_deadlines_to_json(db, user_id))

        return {
            "export_date": datetime.now().isoformat(),
            "user_id": str(user_id) if user_id else None,
            "summary": {
                "total_notes": notes_json["total_notes"],
                "total_conversations": conversations_json["total_conversations"],
                "total_deadlines": deadlines_json["total_deadlines"],
            },
            "notes": notes_json["notes"],
            "conversations": conversations_json["conversations"],
            "deadlines": deadlines_json["deadlines"],
        }


# 全局实例
export_service = ExportService()
