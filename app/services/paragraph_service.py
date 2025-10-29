import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from app.schemas.schemas import ParagraphCreate, ParagraphResponse, FetchResponse
from app.repositories.paragraph_repository import ParagraphRepository


logger = logging.getLogger(__name__)


class ParagraphService:
    """Service layer for paragraph business logic."""
    
    def __init__(self):
        self.repository = ParagraphRepository()
    
    async def fetch_and_store_paragraph(
        self, 
        db: AsyncSession, 
        api_url: str,
        timeout: float = 30.0
    ) -> FetchResponse:
        """
        Fetch a paragraph from external API and store it in database.
        
        Args:
            db: Database session
            api_url: URL to fetch paragraph from
            timeout: Request timeout in seconds
            
        Returns:
            FetchResponse with stored paragraph
            
        Raises:
            httpx.TimeoutException: If request times out
            httpx.HTTPStatusError: If API returns error status
            httpx.RequestError: If network error occurs
            Exception: If database operation fails
        """
        logger.info(f"Fetching paragraph from: {api_url}")
        
        # Configure httpx client with timeout
        timeout_config = httpx.Timeout(timeout)
        
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            # Fetch paragraph from external API
            response = await client.get(api_url)
            response.raise_for_status()
            
            # Get the text content
            paragraph_text = response.text.strip()
            
            if not paragraph_text:
                raise ValueError("Empty response from external API")
            
            logger.info(f"Successfully fetched paragraph with {len(paragraph_text)} characters")
        
        # Store paragraph in database
        try:
            paragraph_create = ParagraphCreate(text=paragraph_text)
            stored_paragraph = await self.repository.create(db, paragraph_create)
            
            logger.info(f"Successfully stored paragraph with ID: {stored_paragraph.id}")
            
            return FetchResponse(
                paragraph=stored_paragraph,
                message="Paragraph fetched and stored successfully"
            )
            
        except Exception as e:
            logger.error(f"Database error while storing paragraph: {e}")
            raise
    
    async def search_paragraphs(
        self, 
        db: AsyncSession, 
        words: List[str], 
        operator: str = "or"
    ) -> List[ParagraphResponse]:
        """
        Search paragraphs using full-text search.
        
        Args:
            db: Database session
            words: List of words to search for
            operator: 'and' or 'or' for combining search terms
            
        Returns:
            List of matching paragraphs
        """
        logger.info(f"Searching for words: {words} with operator: {operator}")
        
        if not words:
            return []
        
        try:
            matching_paragraphs = await self.repository.search_by_text(
                db=db,
                words=words,
                operator=operator
            )
            
            logger.info(f"Found {len(matching_paragraphs)} matching paragraphs")
            return matching_paragraphs
            
        except Exception as e:
            logger.error(f"Error during paragraph search: {e}")
            raise
    
    
    async def get_paragraph_count(self, db: AsyncSession) -> int:
        """Get total count of paragraphs."""
        return await self.repository.count(db)
    