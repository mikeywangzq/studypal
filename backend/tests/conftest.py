"""
Pytest configuration and fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():
    """Create a new database session for a test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_note_data():
    """Sample note data for testing"""
    return {
        "title": "测试笔记.md",
        "file_type": "md",
        "content": """# 测试笔记

这是一个测试笔记，用于验证系统功能。

## 操作系统概念

操作系统是管理计算机硬件和软件资源的程序。

主要功能包括：
- 进程管理
- 内存管理
- 文件系统管理
- 设备管理

## 关键概念

- **进程**: 正在执行的程序实例
- **线程**: 进程中的执行单元
- **虚拟内存**: 将磁盘空间作为内存使用
""",
        "category": "操作系统",
        "tags": ["操作系统", "进程", "内存"]
    }
