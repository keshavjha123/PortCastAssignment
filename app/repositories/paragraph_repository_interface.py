from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import Paragraph
from app.schemas.schemas import ParagraphCreate


class ParagraphRepositoryInterface(ABC):
    """Abstract interface for paragraph repository operations."""
    
    @abstractmethod
    async def create(self, db: AsyncSession, paragraph: ParagraphCreate) -> Paragraph:
        pass
    
    @abstractmethod
    async def count(self, db: AsyncSession) -> int:
        pass
    
    @abstractmethod
    async def search_by_text(self, db: AsyncSession, words: List[str], operator: str = "or") -> List[Paragraph]:
        pass
    