"""
Notes API endpoints
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..database import get_db
from ..schemas.note import NoteResponse, NoteListResponse, NoteUpdate
from ..services.note_service import note_service
from ..utils.file_handler import is_supported_file, get_file_type, save_uploaded_file
from ..config import settings

router = APIRouter()


@router.post("/upload", response_model=dict)
async def upload_notes(
    files: List[UploadFile] = File(...),
    auto_classify: bool = Query(False, description="自动分类和提取标签"),
    db: Session = Depends(get_db)
):
    """
    Upload one or more note files

    - **files**: List of files to upload (markdown, code files, etc.)
    - **auto_classify**: Enable automatic classification and tag extraction using LLM
    """
    success_count = 0
    failed_count = 0
    note_ids = []
    errors = []

    total_size = sum(file.size or 0 for file in files)
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if total_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"Total file size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit"
        )

    for file in files:
        try:
            # Validate file type
            if not is_supported_file(file.filename):
                failed_count += 1
                errors.append(f"{file.filename}: Unsupported file type")
                continue

            # Validate file size
            if file.size and file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                failed_count += 1
                errors.append(f"{file.filename}: File size exceeds {settings.MAX_FILE_SIZE_MB}MB")
                continue

            # Read file content
            content = await file.read()

            # Save file to disk
            file_path, content_str = save_uploaded_file(
                content,
                file.filename,
                user_id="default"  # TODO: Get from auth
            )

            # Create note with embeddings
            from ..schemas.note import NoteCreate
            note_create = NoteCreate(
                title=file.filename,
                file_type=get_file_type(file.filename),
                content=content_str,
                category=None,  # Will be set by auto-classification if enabled
                tags=[]
            )

            note = await note_service.create_note_with_chunks(
                db=db,
                note_create=note_create,
                file_path=file_path,
                user_id=None,  # TODO: Get from auth
                auto_classify=auto_classify
            )

            note_ids.append(str(note.id))
            success_count += 1

        except Exception as e:
            failed_count += 1
            errors.append(f"{file.filename}: {str(e)}")

    return {
        "note_ids": note_ids,
        "success_count": success_count,
        "failed_count": failed_count,
        "errors": errors if errors else None
    }


@router.get("", response_model=NoteListResponse)
def get_notes(
    category: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),  # Comma-separated tags
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get list of notes with optional filters

    - **category**: Filter by category
    - **tags**: Filter by tags (comma-separated)
    - **page**: Page number (starts from 1)
    - **limit**: Number of items per page
    """
    skip = (page - 1) * limit
    tag_list = tags.split(',') if tags else None

    notes, total = note_service.get_notes(
        db=db,
        user_id=None,  # TODO: Get from auth
        category=category,
        tags=tag_list,
        skip=skip,
        limit=limit
    )

    return NoteListResponse(
        notes=[NoteResponse.model_validate(note) for note in notes],
        total=total,
        page=page,
        limit=limit
    )


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific note by ID
    """
    note = note_service.get_note(db=db, note_id=note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return NoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: UUID,
    note_update: NoteUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a note

    - **title**: New title
    - **category**: New category
    - **tags**: New tags
    - **content**: New content (will regenerate embeddings if changed)
    """
    note = note_service.update_note(
        db=db,
        note_id=note_id,
        note_update=note_update
    )

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # TODO: If content changed, regenerate embeddings

    return NoteResponse.model_validate(note)


@router.delete("/{note_id}")
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a note
    """
    success = note_service.delete_note(db=db, note_id=note_id)

    if not success:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"message": "Note deleted successfully"}


@router.get("/search/", response_model=List[dict])
def search_notes(
    query: str = Query(..., min_length=1),
    k: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Search notes using semantic search

    - **query**: Search query
    - **k**: Number of results to return
    """
    results = note_service.search_notes(
        db=db,
        query=query,
        user_id=None,  # TODO: Get from auth
        k=k
    )

    return [
        {
            "note": NoteResponse.model_validate(result["note"]),
            "content_snippet": result["content_snippet"],
            "score": result["score"]
        }
        for result in results
    ]


@router.get("/categories/available", response_model=List[str])
def get_available_categories():
    """
    获取所有可用的笔记分类

    返回预定义的分类列表，用于前端展示和筛选
    """
    from ..services.classification_service import classification_service
    return classification_service.get_available_categories()
