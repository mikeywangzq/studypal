"""
WebSocket Manager - WebSocket 实时协作管理器

管理WebSocket连接的生命周期：
1. 连接建立 - 用户加入笔记编辑
2. 消息广播 - 光标位置、编辑操作
3. 连接断开 - 用户离开编辑
4. 状态管理 - 在线用户、光标位置

数据结构设计：
- active_connections: 二维字典，笔记ID -> {用户ID -> WebSocket连接}
- cursor_positions: 二维字典，笔记ID -> {用户ID -> {line, column}}

优势：
- O(1)时间复杂度查找连接
- 自动隔离不同笔记的用户
- 支持同一用户编辑多个笔记
"""
from typing import Dict, List, Set
from fastapi import WebSocket
from uuid import UUID
import json
import asyncio
import logging

# 配置日志
logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket 连接管理器

    负责管理所有笔记的实时协作连接
    采用房间模式：每个笔记是一个独立的房间
    """

    def __init__(self):
        # 存储活跃连接: note_id -> {user_id: websocket}
        # 例如: {note1_id: {user1_id: ws1, user2_id: ws2}}
        self.active_connections: Dict[UUID, Dict[UUID, WebSocket]] = {}

        # 存储用户光标位置: note_id -> {user_id: {line, column}}
        # 例如: {note1_id: {user1_id: {line: 10, column: 5}}}
        # 注意：光标位置存储在内存中，服务器重启后会丢失
        self.cursor_positions: Dict[UUID, Dict[UUID, dict]] = {}

    async def connect(self, websocket: WebSocket, note_id: UUID, user_id: UUID, username: str):
        """
        连接用户到笔记（加入协作房间）

        流程：
        1. 接受WebSocket连接
        2. 将连接存储到活跃连接字典
        3. 广播"用户加入"消息给其他在线用户
        4. 发送当前在线用户列表给新用户（包括光标位置）

        Args:
            websocket: WebSocket 连接对象
            note_id: 笔记ID（房间ID）
            user_id: 用户ID
            username: 用户名（用于显示）
        """
        # 接受WebSocket连接
        await websocket.accept()
        logger.info(f"用户 {username}({user_id}) 正在加入笔记 {note_id}")

        # 如果笔记房间不存在，创建新房间
        if note_id not in self.active_connections:
            self.active_connections[note_id] = {}
            self.cursor_positions[note_id] = {}
            logger.info(f"创建新的协作房间: {note_id}")

        # 存储连接
        self.active_connections[note_id][user_id] = websocket

        # 通知其他用户有新用户加入
        await self.broadcast_to_note(note_id, {
            'type': 'user_joined',
            'user_id': str(user_id),
            'username': username,
            'users_count': len(self.active_connections[note_id])
        }, exclude_user=user_id)

        # 发送当前在线用户列表给新用户（包括他们的光标位置）
        online_users = [
            {
                'user_id': str(uid),
                'cursor': self.cursor_positions[note_id].get(uid)
            }
            for uid in self.active_connections[note_id].keys()
            if uid != user_id  # 排除自己
        ]

        await websocket.send_json({
            'type': 'online_users',
            'users': online_users
        })

        logger.info(f"用户 {username}({user_id}) 已加入笔记 {note_id}，当前在线: {len(self.active_connections[note_id])} 人")

    def disconnect(self, note_id: UUID, user_id: UUID):
        """
        断开用户连接（离开协作房间）

        清理流程：
        1. 从活跃连接字典中移除用户
        2. 清除用户的光标位置
        3. 如果房间已空，删除整个房间数据（节省内存）

        注意：此方法是同步的，不发送通知
        通知应在调用此方法后由业务逻辑发送

        Args:
            note_id: 笔记ID
            user_id: 用户ID
        """
        if note_id in self.active_connections:
            # 移除用户连接
            if user_id in self.active_connections[note_id]:
                del self.active_connections[note_id][user_id]
                logger.info(f"用户 {user_id} 已断开与笔记 {note_id} 的连接")

            # 清除光标位置
            if user_id in self.cursor_positions.get(note_id, {}):
                del self.cursor_positions[note_id][user_id]

            # 如果房间已空，清理房间数据
            if not self.active_connections[note_id]:
                del self.active_connections[note_id]
                if note_id in self.cursor_positions:
                    del self.cursor_positions[note_id]
                logger.info(f"协作房间 {note_id} 已空，已清理")

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
        向笔记的所有在线用户广播消息

        用途：
        - 广播光标位置更新
        - 广播编辑操作
        - 广播用户加入/离开事件

        特点：
        - 自动检测并清理失效的连接
        - 支持排除特定用户（如排除消息发送者本人）

        Args:
            note_id: 笔记ID（房间ID）
            message: 要广播的消息字典（将转换为JSON）
            exclude_user: 要排除的用户ID（可选，通常是消息发送者）
        """
        if note_id not in self.active_connections:
            logger.warning(f"笔记 {note_id} 没有活跃连接")
            return

        disconnected_users = []  # 记录发送失败的用户

        # 向房间内所有用户发送消息
        for user_id, connection in self.active_connections[note_id].items():
            # 如果指定了排除用户，跳过该用户
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await connection.send_json(message)
            except Exception as e:
                # 发送失败，说明连接已断开
                logger.warning(f"发送消息失败，连接可能已断开: user_id={user_id}, error={e}")
                disconnected_users.append(user_id)

        # 清理断开的连接
        for user_id in disconnected_users:
            self.disconnect(note_id, user_id)
            logger.info(f"已清理断开的连接: user_id={user_id}")

    async def update_cursor_position(
        self,
        note_id: UUID,
        user_id: UUID,
        username: str,
        line: int,
        column: int
    ):
        """
        更新并广播用户的光标位置

        用户在编辑器中移动光标时调用此方法
        会将光标位置存储并广播给其他在线用户
        其他用户可以看到协作者的光标位置

        Args:
            note_id: 笔记ID
            user_id: 用户ID
            username: 用户名（用于显示）
            line: 光标所在行号（从0或1开始，取决于前端实现）
            column: 光标所在列号
        """
        # 如果笔记房间不存在，创建它（边界情况处理）
        if note_id not in self.cursor_positions:
            self.cursor_positions[note_id] = {}

        # 更新光标位置（存储在内存中）
        self.cursor_positions[note_id][user_id] = {
            'line': line,
            'column': column
        }

        # 广播光标位置给其他用户（排除自己）
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
        广播编辑操作到其他用户

        用户修改文本时调用此方法
        将编辑操作（插入、删除、替换）广播给其他在线用户
        其他用户可以实时看到文本变化

        编辑操作格式示例：
        {
            'type': 'insert',  # 或 'delete', 'replace'
            'position': {'line': 10, 'column': 5},
            'content': '新插入的文本',
            'length': 6  # 对于delete操作
        }

        Args:
            note_id: 笔记ID
            user_id: 编辑者用户ID
            username: 编辑者用户名
            operation: 编辑操作详情（字典格式）
        """
        await self.broadcast_to_note(note_id, {
            'type': 'edit',
            'user_id': str(user_id),
            'username': username,
            'operation': operation
        }, exclude_user=user_id)  # 不发送给操作者本人

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
