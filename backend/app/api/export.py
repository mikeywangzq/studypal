"""
Export API endpoints - 数据导出接口
"""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from ..database import get_db
from ..services.export_service import export_service
from ..dependencies import get_current_active_user
from ..models.user import User

router = APIRouter()


@router.get("/notes/json")
async def export_notes_json(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    导出笔记为 JSON 格式

    需要认证。导出当前用户的所有笔记。
    """
    json_data = export_service.export_notes_to_json(db, current_user.id)

    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=studypal_notes_{current_user.username}.json"
        }
    )


@router.get("/notes/markdown")
async def export_notes_markdown(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    导出笔记为 Markdown 格式

    需要认证。导出当前用户的所有笔记为一个 Markdown 文件。
    """
    markdown_data = export_service.export_notes_to_markdown(db, current_user.id)

    return Response(
        content=markdown_data.encode('utf-8'),
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=studypal_notes_{current_user.username}.md"
        }
    )


@router.get("/conversations/json")
async def export_conversations_json(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    导出对话为 JSON 格式

    需要认证。导出当前用户的所有对话记录。
    """
    json_data = export_service.export_conversations_to_json(db, current_user.id)

    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=studypal_conversations_{current_user.username}.json"
        }
    )


@router.get("/deadlines/json")
async def export_deadlines_json(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    导出 DDL 为 JSON 格式

    需要认证。导出当前用户的所有截止日期。
    """
    json_data = export_service.export_deadlines_to_json(db, current_user.id)

    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=studypal_deadlines_{current_user.username}.json"
        }
    )


@router.get("/deadlines/csv")
async def export_deadlines_csv(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    导出 DDL 为 CSV 格式

    需要认证。导出当前用户的所有截止日期为 CSV 文件。
    可以在 Excel 或 Google Sheets 中打开。
    """
    csv_data = export_service.export_deadlines_to_csv(db, current_user.id)

    return Response(
        content=csv_data.encode('utf-8-sig'),  # 使用 UTF-8 with BOM 以支持 Excel
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=studypal_deadlines_{current_user.username}.csv"
        }
    )


@router.get("/all/json")
async def export_all_data_json(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    导出所有数据为 JSON 格式

    需要认证。导出当前用户的所有数据（笔记、对话、DDL）为一个 JSON 文件。

    **用途**:
    - 数据备份
    - 数据迁移
    - 数据分析
    """
    all_data = export_service.export_all_data(db, current_user.id)

    import json
    json_data = json.dumps(all_data, ensure_ascii=False, indent=2)

    return Response(
        content=json_data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=studypal_all_data_{current_user.username}.json"
        }
    )
