"""
Collaboration API endpoints - 协作功能API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import json

from ..database import get_db
from ..dependencies import get_current_active_user, get_optional_current_user
from ..models.user import User
from ..models.note import Note
from ..schemas.collaboration import (
    NoteVersionResponse,
    NoteVersionWithUser,
    VersionCompareResponse,
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentWithUser,
    NotificationResponse,
    NotificationWithActor,
    NotificationStats,
)
from ..services.version_service import version_service
from ..services.comment_service import comment_service
from ..services.notification_service import notification_service
from ..services.websocket_manager import manager
from ..services.share_service import share_service

router = APIRouter()


# ========== 版本历史 API ==========

@router.get("/notes/{note_id}/versions", response_model=List[NoteVersionWithUser])
async def get_note_versions(
    note_id: UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取笔记的版本历史

    需要有笔记的查看权限
    """
    # 检查权限
    has_access = share_service.check_user_access(db, note_id, current_user.id, 'view')
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看此笔记"
        )

    versions = version_service.get_note_versions(db, note_id, limit)

    results = []
    for version in versions:
        user = db.query(User).filter(User.id == version.changed_by).first() if version.changed_by else None

        results.append(NoteVersionWithUser(
            id=version.id,
            note_id=version.note_id,
            version_number=version.version_number,
            title=version.title,
            content=version.content,
            category=version.category,
            tags=json.loads(version.tags) if version.tags else [],
            changed_by=version.changed_by,
            changed_by_username=user.username if user else None,
            change_description=version.change_description,
            created_at=version.created_at
        ))

    return results


@router.post("/notes/{note_id}/versions", response_model=NoteVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_note_version(
    note_id: UUID,
    change_description: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    手动创建笔记版本快照

    需要有笔记的编辑权限
    """
    # 检查权限
    has_access = share_service.check_user_access(db, note_id, current_user.id, 'edit')
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限编辑此笔记"
        )

    version = version_service.create_version(db, note_id, current_user.id, change_description)

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )

    return NoteVersionResponse.model_validate(version)


@router.post("/notes/{note_id}/restore/{version_id}", status_code=status.HTTP_200_OK)
async def restore_note_version(
    note_id: UUID,
    version_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    恢复到指定版本

    需要有笔记的编辑权限
    """
    # 检查权限
    has_access = share_service.check_user_access(db, note_id, current_user.id, 'edit')
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限编辑此笔记"
        )

    success = version_service.restore_version(db, note_id, version_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在或恢复失败"
        )

    return {"message": "版本恢复成功"}


@router.get("/versions/compare")
async def compare_versions(
    version_id1: UUID,
    version_id2: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    对比两个版本

    需要有笔记的查看权限
    """
    result = version_service.compare_versions(db, version_id1, version_id2)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在或不属于同一笔记"
        )

    # 检查权限
    has_access = share_service.check_user_access(db, result['version1'].note_id, current_user.id, 'view')
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限查看此笔记"
        )

    return result


# ========== 评论 API ==========

@router.post("/notes/{note_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    note_id: UUID,
    comment_create: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建评论

    需要有笔记的查看权限
    """
    # 检查权限
    has_access = share_service.check_user_access(db, note_id, current_user.id, 'view')
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问此笔记"
        )

    comment = comment_service.create_comment(db, note_id, current_user.id, comment_create)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在或父评论不存在"
        )

    # 发送通知
    note = db.query(Note).filter(Note.id == note_id).first()
    if note and note.user_id != current_user.id:
        # 通知笔记所有者
        notification_service.notify_comment(
            db,
            note.user_id,
            note.title,
            current_user.id,
            note_id,
            comment.id
        )

    # 通知被提及的用户
    if comment_create.mentions:
        for mentioned_user_id in comment_create.mentions:
            if mentioned_user_id != current_user.id:
                notification_service.notify_mention(
                    db,
                    mentioned_user_id,
                    note.title,
                    current_user.id,
                    comment.id
                )

    return CommentResponse.model_validate(comment)


@router.get("/notes/{note_id}/comments", response_model=List[CommentWithUser])
async def get_note_comments(
    note_id: UUID,
    current_user: User = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    获取笔记的所有评论

    支持公开访问（通过分享令牌）
    """
    # 如果已登录，检查权限
    if current_user:
        has_access = share_service.check_user_access(db, note_id, current_user.id, 'view')
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您没有权限访问此笔记"
            )
    else:
        # 未登录用户，检查笔记是否存在
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="笔记不存在"
            )

    comments = comment_service.get_note_comments(db, note_id, include_replies=False)

    # 构建评论树
    results = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()

        comment_data = CommentWithUser(
            id=comment.id,
            note_id=comment.note_id,
            user_id=comment.user_id,
            username=user.username if user else "Unknown",
            avatar_url=user.avatar_url if user else None,
            content=comment.content,
            parent_id=comment.parent_id,
            mentions=json.loads(comment.mentions) if comment.mentions else [],
            is_edited=comment.is_edited,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[]
        )

        # 获取回复
        replies = comment_service.get_comment_replies(db, comment.id)
        for reply in replies:
            reply_user = db.query(User).filter(User.id == reply.user_id).first()
            comment_data.replies.append(CommentWithUser(
                id=reply.id,
                note_id=reply.note_id,
                user_id=reply.user_id,
                username=reply_user.username if reply_user else "Unknown",
                avatar_url=reply_user.avatar_url if reply_user else None,
                content=reply.content,
                parent_id=reply.parent_id,
                mentions=json.loads(reply.mentions) if reply.mentions else [],
                is_edited=reply.is_edited,
                created_at=reply.created_at,
                updated_at=reply.updated_at,
                replies=[]
            ))

        results.append(comment_data)

    return results


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新评论

    只有评论作者可以更新
    """
    comment = comment_service.update_comment(db, comment_id, current_user.id, comment_update)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或您没有权限"
        )

    return CommentResponse.model_validate(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除评论

    只有评论作者可以删除
    """
    success = comment_service.delete_comment(db, comment_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在或您没有权限"
        )

    return None


# ========== 通知 API ==========

@router.get("/notifications", response_model=List[NotificationWithActor])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的通知列表
    """
    notifications = notification_service.get_user_notifications(
        db,
        current_user.id,
        unread_only,
        limit
    )

    results = []
    for notification in notifications:
        actor = db.query(User).filter(User.id == notification.actor_id).first() if notification.actor_id else None

        results.append(NotificationWithActor(
            id=notification.id,
            user_id=notification.user_id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            resource_type=notification.resource_type,
            resource_id=notification.resource_id,
            actor_id=notification.actor_id,
            actor_username=actor.username if actor else None,
            actor_avatar_url=actor.avatar_url if actor else None,
            is_read=notification.is_read,
            created_at=notification.created_at,
            read_at=notification.read_at
        ))

    return results


@router.post("/notifications/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记通知为已读
    """
    success = notification_service.mark_as_read(db, notification_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )

    return {"message": "已标记为已读"}


@router.post("/notifications/read-all", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记所有通知为已读
    """
    count = notification_service.mark_all_as_read(db, current_user.id)

    return {"message": f"已标记 {count} 条通知为已读"}


@router.get("/notifications/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取通知统计
    """
    stats = notification_service.get_notification_stats(db, current_user.id)

    return NotificationStats(
        total=stats['total'],
        unread=stats['unread'],
        by_type=stats['by_type']
    )


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除通知
    """
    success = notification_service.delete_notification(db, notification_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )

    return None


# ========== WebSocket 实时协作 ==========

@router.websocket("/ws/notes/{note_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    note_id: UUID,
    user_id: UUID,
    username: str
):
    """
    WebSocket 实时协作端点

    连接参数:
    - note_id: 笔记ID
    - user_id: 用户ID
    - username: 用户名

    消息类型:
    - cursor_update: 光标位置更新
    - edit: 编辑操作
    - user_joined: 用户加入
    - user_left: 用户离开
    """
    await manager.connect(websocket, note_id, user_id, username)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()

            message_type = data.get('type')

            if message_type == 'cursor_update':
                # 更新光标位置
                position = data.get('position', {})
                await manager.update_cursor_position(
                    note_id,
                    user_id,
                    username,
                    position.get('line', 0),
                    position.get('column', 0)
                )

            elif message_type == 'edit':
                # 广播编辑操作
                operation = data.get('operation', {})
                await manager.broadcast_edit(
                    note_id,
                    user_id,
                    username,
                    operation
                )

    except WebSocketDisconnect:
        manager.disconnect(note_id, user_id)

        # 通知其他用户
        await manager.broadcast_to_note(note_id, {
            'type': 'user_left',
            'user_id': str(user_id),
            'username': username,
            'users_count': manager.get_user_count(note_id)
        })


@router.get("/notes/{note_id}/online-users")
async def get_online_users(
    note_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取笔记的在线用户列表
    """
    # 检查权限
    has_access = share_service.check_user_access(db, note_id, current_user.id, 'view')
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问此笔记"
        )

    online_users = manager.get_online_users(note_id)

    return {
        'note_id': str(note_id),
        'online_users': [str(uid) for uid in online_users],
        'users_count': len(online_users)
    }
