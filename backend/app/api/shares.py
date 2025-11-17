"""
Note Sharing API endpoints - 笔记分享API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dependencies import get_current_active_user
from ..models.user import User
from ..models.note import Note
from ..schemas.share import (
    NoteShareCreate,
    NoteShareUpdate,
    NoteShareResponse,
    NoteShareWithDetails,
    NotePermissionCreate,
    NotePermissionUpdate,
    NotePermissionResponse,
    NotePermissionWithDetails,
    SharedNoteResponse,
)
from ..services.share_service import share_service

router = APIRouter()


# ========== 笔记分享管理 ==========

@router.post("/notes/{note_id}/share", response_model=NoteShareResponse, status_code=status.HTTP_201_CREATED)
async def create_note_share(
    note_id: UUID,
    share_create: NoteShareCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建笔记分享

    - **note_id**: 笔记ID
    - **shared_with**: 被分享者用户ID（null表示公开分享）
    - **permission**: 分享权限（view 或 edit）
    - **expires_at**: 过期时间（可选）

    返回分享链接的token，可以通过 `/api/shares/token/{share_token}` 访问
    """
    share = share_service.create_share(
        db,
        note_id,
        current_user.id,
        share_create
    )

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在或您没有分享权限"
        )

    return NoteShareResponse.model_validate(share)


@router.get("/notes/{note_id}/shares", response_model=List[NoteShareResponse])
async def get_note_shares(
    note_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取笔记的所有分享

    仅笔记所有者可以查看
    """
    shares = share_service.get_note_shares(db, note_id, current_user.id)
    return [NoteShareResponse.model_validate(share) for share in shares]


@router.get("/shares/token/{share_token}")
async def get_shared_note_by_token(
    share_token: str,
    db: Session = Depends(get_db)
):
    """
    通过分享令牌访问笔记

    **公开端点** - 无需认证，任何人持有token即可访问
    """
    share = share_service.get_share_by_token(db, share_token)

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享不存在、已过期或已停用"
        )

    # 获取笔记信息
    note = db.query(Note).filter(Note.id == share.note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )

    return {
        "share": NoteShareResponse.model_validate(share),
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "category": note.category,
            "tags": note.tags,
            "file_type": note.file_type,
            "created_at": note.created_at,
        },
        "permission": share.permission.value
    }


@router.put("/shares/{share_id}", response_model=NoteShareResponse)
async def update_share(
    share_id: UUID,
    share_update: NoteShareUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新分享设置

    仅分享创建者可以更新
    """
    share = share_service.update_share(db, share_id, current_user.id, share_update)

    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享不存在或您没有权限"
        )

    return NoteShareResponse.model_validate(share)


@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_share(
    share_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    取消分享

    仅分享创建者可以取消
    """
    success = share_service.delete_share(db, share_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="分享不存在或您没有权限"
        )

    return None


@router.get("/notes/shared-with-me", response_model=List[SharedNoteResponse])
async def get_shared_with_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取分享给我的所有笔记

    返回其他用户分享给当前用户的所有笔记
    """
    shares = share_service.get_shared_with_me(db, current_user.id)

    results = []
    for share in shares:
        note = db.query(Note).filter(Note.id == share.note_id).first()
        if note:
            # 获取分享者用户名
            sharer = db.query(User).filter(User.id == share.shared_by).first()

            results.append(SharedNoteResponse(
                note_id=note.id,
                title=note.title,
                category=note.category,
                tags=note.tags or [],
                permission=share.permission.value,
                shared_by=share.shared_by,
                shared_by_username=sharer.username if sharer else "Unknown",
                share_token=share.share_token,
                created_at=share.created_at,
                file_type=note.file_type
            ))

    return results


# ========== 笔记权限管理 ==========

@router.post("/notes/{note_id}/permissions", response_model=NotePermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_note_permission(
    note_id: UUID,
    permission_create: NotePermissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    为用户添加笔记权限

    仅笔记所有者可以添加权限

    **权限级别**:
    - **owner**: 所有者（完全控制）
    - **editor**: 编辑者（可编辑）
    - **viewer**: 查看者（只读）
    """
    permission = share_service.create_permission(
        db,
        note_id,
        current_user.id,
        permission_create
    )

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在或您没有权限"
        )

    return NotePermissionResponse.model_validate(permission)


@router.get("/notes/{note_id}/permissions", response_model=List[NotePermissionWithDetails])
async def get_note_permissions(
    note_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取笔记的所有权限

    仅笔记所有者可以查看
    """
    permissions = share_service.get_note_permissions(db, note_id, current_user.id)

    results = []
    for perm in permissions:
        user = db.query(User).filter(User.id == perm.user_id).first()
        granter = db.query(User).filter(User.id == perm.granted_by).first() if perm.granted_by else None

        results.append(NotePermissionWithDetails(
            id=perm.id,
            note_id=perm.note_id,
            user_id=perm.user_id,
            username=user.username if user else "Unknown",
            email=user.email if user else "",
            permission_level=perm.permission_level.value,
            granted_by=perm.granted_by,
            granted_by_username=granter.username if granter else None,
            created_at=perm.created_at
        ))

    return results


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    移除用户权限

    仅笔记所有者可以移除权限
    """
    success = share_service.delete_permission(db, permission_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在或您没有权限"
        )

    return None


@router.get("/notes/{note_id}/check-access")
async def check_note_access(
    note_id: UUID,
    permission: str = "view",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    检查当前用户是否有权限访问笔记

    **permission**: 'view' 或 'edit'
    """
    has_access = share_service.check_user_access(
        db,
        note_id,
        current_user.id,
        permission
    )

    return {
        "note_id": note_id,
        "user_id": current_user.id,
        "required_permission": permission,
        "has_access": has_access
    }
