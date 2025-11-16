"""
Text splitting utilities for chunking documents
"""
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..config import settings


def create_text_splitter(chunk_size: int = None, chunk_overlap: int = None) -> RecursiveCharacterTextSplitter:
    """
    Create a text splitter for chunking documents

    Args:
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks

    Returns:
        RecursiveCharacterTextSplitter instance
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    )


def split_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    """
    Split text into chunks

    Args:
        text: Text to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    splitter = create_text_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_text(text)
    return chunks


def split_text_with_metadata(text: str, metadata: dict = None) -> List[dict]:
    """
    Split text into chunks with metadata

    Args:
        text: Text to split
        metadata: Metadata to attach to each chunk

    Returns:
        List of dictionaries with 'text' and 'metadata' keys
    """
    chunks = split_text(text)
    metadata = metadata or {}

    return [
        {
            "text": chunk,
            "metadata": {**metadata, "chunk_index": i}
        }
        for i, chunk in enumerate(chunks)
    ]
