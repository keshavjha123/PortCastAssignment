import os
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, Index
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql import func

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/portcast_api")

# Convert sync URL to async URL for asyncpg  
# Handle both postgres:// and postgresql:// prefixes from cloud providers
if DATABASE_URL.startswith("postgres://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Convert sslmode=require to ssl=require for asyncpg compatibility
if "sslmode=require" in ASYNC_DATABASE_URL:
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("sslmode=require", "ssl=require")

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()


class Paragraph(Base):
    __tablename__ = "paragraphs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Full-text search vector column
    search_vector = Column(TSVECTOR)
    
    __table_args__ = (
        Index('ix_paragraphs_search_vector', 'search_vector', postgresql_using='gin'),
    )


async def get_db():
    """Dependency to get async database session."""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def init_db():
    """Initialize database with required extensions and triggers."""
    from sqlalchemy import text
    
    async with engine.begin() as conn:
        # Create trigram extension if it doesn't exist
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
    
    # Create tables after extensions are installed
    await create_tables()
    
    async with engine.begin() as conn:
        # Create or replace function to update search vector
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_search_vector()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.search_vector := to_tsvector('english', NEW.text);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        # Drop trigger if it exists and create new one
        await conn.execute(text("DROP TRIGGER IF EXISTS update_paragraph_search_vector ON paragraphs;"))
        await conn.execute(text("""
            CREATE TRIGGER update_paragraph_search_vector
            BEFORE INSERT OR UPDATE ON paragraphs
            FOR EACH ROW EXECUTE FUNCTION update_search_vector();
        """))
        
        # Create additional indexes after table creation
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_paragraphs_text_gin 
            ON paragraphs USING gin (text gin_trgm_ops);
        """))