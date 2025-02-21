import pytest
import pytest_asyncio
import asyncio
import platform
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.core.config import get_settings
from src.main import app
from src.models.message import Base
from src.core.database import get_db
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from src.core.auth import create_access_token, create_api_key

@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create engine instance for all tests."""
    settings = get_settings()
    test_db_url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    
    engine = create_async_engine(
        test_db_url,
        echo=True,
        poolclass=NullPool,
        connect_args={
            "command_timeout": 60,
            "server_settings": {
                "application_name": "whatsapp_bot_test",
                "statement_timeout": "60000"
            }
        }
    )
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield engine
    finally:
        await engine.dispose()

@pytest_asyncio.fixture  # Remove the duplicate decorator
async def test_db(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for a test."""
    session_maker = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    async with session_maker() as session:
        try:
            # Test the session
            await session.execute(text("SELECT 1"))
            await session.commit()
            
            yield session
        finally:
            await session.rollback()
            await session.close()

@pytest.fixture
def test_client(test_db: AsyncSession) -> TestClient:
    """Create a test client with database session."""
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def clean_db(test_db: AsyncSession) -> None:
    from sqlalchemy import text
    await test_db.execute(text("TRUNCATE users, messages, sessions CASCADE;"))
    await test_db.commit()

@pytest.fixture
def test_token():
    """Create a test JWT token"""
    return create_access_token(data={"sub": "test_user"})

@pytest.fixture
def test_api_key():
    """Create a test API key"""
    return create_api_key()

@pytest.fixture
def mock_websocket_client():
    class MockWebSocket:
        def __init__(self):
            self.last_message = None
            self.accepted = False
            
        async def accept(self):
            self.accepted = True
            
        async def send_text(self, data: str):
            self.last_message = data
        
        async def send_json(self, data: dict):
            self.last_message = data
        
        async def receive_text(self) -> str:
            return "{\"type\": \"message\", \"content\": \"test\"}"
        
        async def close(self):
            self.accepted = False

    return MockWebSocket()