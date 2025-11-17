"""
WebSocket Manager - WebSocket 实时协作管理器
"""
from typing import Dict, List, Set
from fastapi import WebSocket
from uuid import UUID
import json
import asyncio


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 存储活跃连接: note_id -> {user_id: websocket}
        self.active_connections: Dict[UUID, Dict[UUID, WebSocket]] = {}

        # 存储用户光标位置: note_id -> {user_id: {line, column}}
        self.cursor_positions: Dict[UUID, Dict[UUID, dict]] = {}

    async def connect(self, websocket: WebSocket, note_id: UUID, user_id: UUID, username: str):
        """
        连接用户到笔记

        Args:
            websocket: WebSocket 连接
            note_id: 笔记ID
            user_id: 用户ID
            username: 用户名
        """
        await websocket.accept()

        if note_id not in self.active_connections:
            self.active_connections[note_id] = {}
            self.cursor_positions[note_id] = {}

        self.active_connections[note_id][user_id] = websocket

        # 通知其他用户有新用户加入
        await self.broadcast_to_note(note_id, {
            'type': 'user_joined',
            'user_id': str(user_id),
            'username': username,
            'users_count': len(self.active_connections[note_id])
        }, exclude_user=user_id)

        # 发送当前在线用户列表给新用户
        online_users = [
            {
                'user_id': str(uid),
                'cursor': self.cursor_positions[note_id].get(uid)
            }
            for uid in self.active_connections[note_id].keys()
            if uid != user_id
        ]

        await websocket.send_json({
            'type': 'online_users',
            'users': online_users
        })

    def disconnect(self, note_id: UUID, user_id: UUID):
        """
        断开用户连接

        Args:
            note_id: 笔记ID
            user_id: 用户ID
        """
        if note_id in self.active_connections:
            if user_id in self.active_connections[note_id]:
                del self.active_connections[note_id][user_id]

            if user_id in self.cursor_positions.get(note_id, {}):
                del self.cursor_positions[note_id][user_id]

            # 如果没有用户了，清理数据
            if not self.active_connections[note_id]:
                del self.active_connections[note_id]
                if note_id in self.cursor_positions:
                    del self.cursor_positions[note_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        发送私人消息

        Args:
            message: 消息内容
            websocket: WebSocket 连接
        """
        await websocket.send_json(message)

    async def broadcast_to_note(
        self,
        note_id: UUID,
        message: dict,
        exclude_user: UUID = None
    ):
        """
        向笔记的所有连接用户广播消息

        Args:
            note_id: 笔记ID
            message: 消息内容
            exclude_user: 排除的用户ID（可选）
        """
        if note_id not in self.active_connections:
            return

        disconnected_users = []

        for user_id, connection in self.active_connections[note_id].items():
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await connection.send_json(message)
            except Exception:
                # 记录断开的连接
                disconnected_users.append(user_id)

        # 清理断开的连接
        for user_id in disconnected_users:
            self.disconnect(note_id, user_id)

    async def update_cursor_position(
        self,
        note_id: UUID,
        user_id: UUID,
        username: str,
        line: int,
        column: int
    ):
        """
        更新并广播光标位置

        Args:
            note_id: 笔记ID
            user_id: 用户ID
            username: 用户名
            line: 行号
            column: 列号
        """
        if note_id not in self.cursor_positions:
            self.cursor_positions[note_id] = {}

        self.cursor_positions[note_id][user_id] = {
            'line': line,
            'column': column
        }

        # 广播光标位置给其他用户
        await self.broadcast_to_note(note_id, {
            'type': 'cursor_update',
            'user_id': str(user_id),
            'username': username,
            'position': {
                'line': line,
                'column': column
            }
        }, exclude_user=user_id)

    async def broadcast_edit(
        self,
        note_id: UUID,
        user_id: UUID,
        username: str,
        operation: dict
    ):
        """
        广播编辑操作

        Args:
            note_id: 笔记ID
            user_id: 用户ID
            username: 用户名
            operation: 编辑操作
        """
        await self.broadcast_to_note(note_id, {
            'type': 'edit',
            'user_id': str(user_id),
            'username': username,
            'operation': operation
        }, exclude_user=user_id)

    def get_online_users(self, note_id: UUID) -> List[UUID]:
        """
        获取笔记的在线用户列表

        Args:
            note_id: 笔记ID

        Returns:
            用户ID列表
        """
        return list(self.active_connections.get(note_id, {}).keys())

    def get_user_count(self, note_id: UUID) -> int:
        """
        获取笔记的在线用户数

        Args:
            note_id: 笔记ID

        Returns:
            在线用户数
        """
        return len(self.active_connections.get(note_id, {}))


# 全局 WebSocket 管理器实例
manager = ConnectionManager()
