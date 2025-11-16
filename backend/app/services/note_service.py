"""
Note service for managing notes and their embeddings
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
import uuid

from ..models.note import Note, NoteChunk
from ..schemas.note import NoteCreate, NoteUpdate
from ..utils.text_splitter import split_text
from .embedding_service import embedding_service


class NoteService:
    """Service for note management"""

    @staticmethod
    async def create_note_with_chunks(
        db: Session,
        note_create: NoteCreate,
        file_path: str,
        user_id: Optional[str] = None
    ) -> Note:
        """
        Create a note and generate embeddings

        Args:
            db: Database session
            note_create: Note creation data
            file_path: Path to the saved file
            user_id: User ID

        Returns:
            Created note
        """
        # Create note
        note = Note(
            id=uuid.uuid4(),
            user_id=UUID(user_id) if user_id else None,
            title=note_create.title,
            file_type=note_create.file_type,
            file_path=file_path,
            content=note_create.content,
            category=note_create.category,
            tags=note_create.tags or []
        )
        db.add(note)
        db.flush()  # Get the note ID

        # Split text into chunks
        chunks = split_text(note_create.content)

        # Generate embeddings and save chunks
        if chunks and embedding_service.vectorstore:
            try:
                chunk_texts = []
                chunk_metadatas = []
                chunk_ids = []

                for i, chunk_text in enumerate(chunks):
                    chunk_id = f"{note.id}_{i}"
                    chunk_texts.append(chunk_text)
                    chunk_metadatas.append({
                        "note_id": str(note.id),
                        "title": note.title,
                        "category": note.category or "",
                        "chunk_index": i
                    })
                    chunk_ids.append(chunk_id)

                # Add to vector store
                vector_ids = embedding_service.add_texts(
                    texts=chunk_texts,
                    metadatas=chunk_metadatas,
                    ids=chunk_ids
                )

                # Save chunks to database
                for i, (chunk_text, vector_id) in enumerate(zip(chunks, vector_ids)):
                    chunk = NoteChunk(
                        id=uuid.uuid4(),
                        note_id=note.id,
                        chunk_index=i,
                        content=chunk_text,
                        vector_id=vector_id
                    )
                    db.add(chunk)

            except Exception as e:
                # If embedding fails, still save the note but log the error
                print(f"Error generating embeddings: {e}")

        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def get_note(db: Session, note_id: UUID) -> Optional[Note]:
        """Get a note by ID"""
        return db.query(Note).filter(Note.id == note_id).first()

    @staticmethod
    def get_notes(
        db: Session,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Note], int]:
        """
        Get notes with filters

        Returns:
            Tuple of (notes, total_count)
        """
        query = db.query(Note)

        if user_id:
            query = query.filter(Note.user_id == UUID(user_id))

        if category:
            query = query.filter(Note.category == category)

        if tags:
            # Filter by tags (PostgreSQL JSONB contains)
            for tag in tags:
                query = query.filter(Note.tags.contains([tag]))

        total = query.count()
        notes = query.order_by(Note.created_at.desc()).offset(skip).limit(limit).all()

        return notes, total

    @staticmethod
    def update_note(
        db: Session,
        note_id: UUID,
        note_update: NoteUpdate
    ) -> Optional[Note]:
        """Update a note"""
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return None

        update_data = note_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(note, key, value)

        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def delete_note(db: Session, note_id: UUID) -> bool:
        """Delete a note and its embeddings"""
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            return False

        # Get all chunk vector IDs
        chunks = db.query(NoteChunk).filter(NoteChunk.note_id == note_id).all()
        vector_ids = [chunk.vector_id for chunk in chunks if chunk.vector_id]

        # Delete from vector store
        if vector_ids:
            embedding_service.delete_by_ids(vector_ids)

        # Delete from database (cascades to chunks)
        db.delete(note)
        db.commit()
        return True

    @staticmethod
    def search_notes(
        db: Session,
        query: str,
        user_id: Optional[str] = None,
        k: int = 5
    ) -> List[dict]:
        """
        Search notes using vector similarity

        Returns:
            List of search results with note info and scores
        """
        filter_dict = {}
        if user_id:
            filter_dict["user_id"] = user_id

        try:
            results = embedding_service.similarity_search(
                query=query,
                k=k,
                filter=filter_dict if filter_dict else None
            )

            search_results = []
            for doc, score in results:
                note_id = doc.metadata.get("note_id")
                if note_id:
                    note = db.query(Note).filter(Note.id == UUID(note_id)).first()
                    if note:
                        search_results.append({
                            "note": note,
                            "content_snippet": doc.page_content,
                            "score": float(score)
                        })

            return search_results

        except Exception as e:
            print(f"Error searching notes: {e}")
            return []


# Global instance
note_service = NoteService()
