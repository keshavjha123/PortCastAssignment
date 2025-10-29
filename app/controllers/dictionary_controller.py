import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.schemas import DictionaryResponse
from app.services.dictionary_service import DictionaryService


logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration
DICTIONARY_API_URL = os.getenv("DICTIONARY_API_URL", "https://api.dictionaryapi.dev/api/v2/entries/en")
HTTP_TIMEOUT = 10.0


class DictionaryController:
    """Controller for dictionary and word analysis operations."""
    
    def __init__(self):
        self.service = DictionaryService()


dictionary_controller = DictionaryController()


@router.get("", response_model=DictionaryResponse)
async def get_dictionary(db: AsyncSession = Depends(get_db)):
    """
    Analyze all stored paragraphs to find the top 10 most frequent words
    and fetch their definitions from the dictionary API.
    
    Args:
        db: Database session
        
    Returns:
        DictionaryResponse: Top 10 words with frequencies and definitions
        
    Raises:
        HTTPException: If database error occurs or no paragraphs found
    """
    try:
        result = await dictionary_controller.service.analyze_word_frequency_with_definitions(
            db=db,
            dictionary_api_url=DICTIONARY_API_URL,
            word_limit=10,
            timeout=HTTP_TIMEOUT
        )
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error in get_dictionary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during dictionary analysis"
        )