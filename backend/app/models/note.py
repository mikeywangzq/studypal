"""
Note and NoteChunk models
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database import Base


class Note(Base):
    """Note model for storing uploaded files"""

    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Nullable for MVP
    title = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # markdown, cpp, python, etc.
    file_path = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True, index=True)  # 操作系统、网络、数据库等
    tags = Column(JSONB, default=list)  # List of tags
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to chunks
    chunks = relationship("NoteChunk", back_populates="note", cascade="all, delete-orphan")


class NoteChunk(Base):
    """NoteChunk model for storing text chunks with embeddings"""

    __tablename__ = "note_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in the note
    content = Column(Text, nullable=False)
    vector_id = Column(String, nullable=True)  # ID in vector database
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to note
    note = relationship("Note", back_populates="chunks")
