import pytest
import asyncio
import os
from typing import AsyncGenerator
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.main import app
from app.database.database import get_db, Base


# Use PostgreSQL for testing (same as production)
# Connect to the same PostgreSQL instance but different database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@db:5432/portcast_test"

# Create async engine for testing
test_async_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False
)

AsyncTestingSessionLocal = async_sessionmaker(
    test_async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for testing."""
    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="session")
async def setup_test_database():
    """Set up the test database with PostgreSQL."""
    # Create test database if it doesn't exist
    admin_engine = create_async_engine(
        "postgresql+asyncpg://postgres:password@db:5432/postgres",
        isolation_level="AUTOCOMMIT"
    )
    
    async with admin_engine.begin() as conn:
        # Check if test database exists, create if not
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'portcast_test'")
        )
        if not result.fetchone():
            await conn.execute(text("CREATE DATABASE portcast_test"))
    
    await admin_engine.dispose()
    
    # Create tables in test database
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Clean up - drop test database
    admin_engine = create_async_engine(
        "postgresql+asyncpg://postgres:password@db:5432/postgres",
        isolation_level="AUTOCOMMIT"
    )
    
    async with admin_engine.begin() as conn:
        # Terminate connections to test database
        await conn.execute(
            text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'portcast_test'
                AND pid <> pg_backend_pid()
            """)
        )
        # Drop test database
        await conn.execute(text("DROP DATABASE IF EXISTS portcast_test"))
    
    await admin_engine.dispose()
    await test_async_engine.dispose()


@pytest_asyncio.fixture
async def async_db_session(setup_test_database) -> AsyncGenerator[AsyncSession, None]:
    """Create an async database session for testing."""
    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture
async def async_client(setup_test_database) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def clean_database(async_db_session: AsyncSession):
    """Clean database before each test."""
    # Clean up any existing data
    await async_db_session.execute(text("TRUNCATE TABLE paragraphs RESTART IDENTITY CASCADE"))
    await async_db_session.commit()
    
    yield
    
    # Clean up after test
    await async_db_session.execute(text("TRUNCATE TABLE paragraphs RESTART IDENTITY CASCADE"))
    await async_db_session.commit()