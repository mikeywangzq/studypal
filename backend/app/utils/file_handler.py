"""
File handling utilities
"""
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Tuple
from ..config import settings


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename

    Args:
        filename: Name of the file

    Returns:
        File extension (e.g., '.md', '.py')
    """
    return Path(filename).suffix


def is_supported_file(filename: str) -> bool:
    """
    Check if file type is supported

    Args:
        filename: Name of the file

    Returns:
        True if supported, False otherwise
    """
    extension = get_file_extension(filename)
    supported = settings.SUPPORTED_EXTENSIONS.split(',')
    return extension.lower() in supported


def get_file_type(filename: str) -> str:
    """
    Get file type from filename

    Args:
        filename: Name of the file

    Returns:
        File type string
    """
    extension = get_file_extension(filename).lower()
    type_mapping = {
        '.md': 'markdown',
        '.txt': 'text',
        '.py': 'python',
        '.cpp': 'cpp',
        '.c': 'c',
        '.java': 'java',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
    }
    return type_mapping.get(extension, 'text')


def generate_file_path(filename: str, user_id: str = "default") -> Tuple[str, str]:
    """
    Generate unique file path for storage

    Args:
        filename: Original filename
        user_id: User ID

    Returns:
        Tuple of (relative_path, absolute_path)
    """
    # Create directory structure: uploads/user_id/YYYY-MM-DD/
    date_str = datetime.now().strftime("%Y-%m-%d")
    relative_dir = os.path.join(user_id, date_str)
    absolute_dir = os.path.join(settings.UPLOAD_DIR, relative_dir)

    # Create directory if it doesn't exist
    os.makedirs(absolute_dir, exist_ok=True)

    # Generate unique filename using hash
    file_hash = hashlib.md5(f"{filename}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{file_hash}{ext}"

    relative_path = os.path.join(relative_dir, unique_filename)
    absolute_path = os.path.join(absolute_dir, unique_filename)

    return relative_path, absolute_path


def save_uploaded_file(file_content: bytes, filename: str, user_id: str = "default") -> Tuple[str, str]:
    """
    Save uploaded file to disk

    Args:
        file_content: File content as bytes
        filename: Original filename
        user_id: User ID

    Returns:
        Tuple of (relative_path, file_content_str)
    """
    relative_path, absolute_path = generate_file_path(filename, user_id)

    # Save file
    with open(absolute_path, 'wb') as f:
        f.write(file_content)

    # Read content as string
    try:
        content_str = file_content.decode('utf-8')
    except UnicodeDecodeError:
        # Try with different encoding
        content_str = file_content.decode('latin-1')

    return relative_path, content_str


def delete_file(file_path: str) -> bool:
    """
    Delete file from disk

    Args:
        file_path: Relative file path

    Returns:
        True if deleted, False otherwise
    """
    try:
        absolute_path = os.path.join(settings.UPLOAD_DIR, file_path)
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
            return True
        return False
    except Exception:
        return False
