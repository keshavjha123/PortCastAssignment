import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.schemas import FetchResponse, ErrorResponse
from app.services.paragraph_service import ParagraphService


logger = logging.getLogger(__name__)
router = APIRouter()

# Configuration
METAPHORPSUM_URL = os.getenv("METAPHORPSUM_URL", "http://metaphorpsum.com/paragraphs/1/50")
HTTP_TIMEOUT = 30.0


class FetchController:
    """Controller for paragraph fetching operations."""
    
    def __init__(self):
        self.service = ParagraphService()


fetch_controller = FetchController()


@router.post("", response_model=FetchResponse)
async def fetch_paragraph(db: AsyncSession = Depends(get_db)):
    """
    Fetch a paragraph with 50 sentences from metaphorpsum.com and store it in the database.
    
    Returns:
        FetchResponse: The fetched and stored paragraph with metadata
        
    Raises:
        HTTPException: If external API is unreachable or database error occurs
    """
    try:
        result = await fetch_controller.service.fetch_and_store_paragraph(
            db=db,
            api_url=METAPHORPSUM_URL,
            timeout=HTTP_TIMEOUT
        )
        return result
        
    except Exception as e:
        logger.error(f"Error in fetch_paragraph: {e}")
        
        # Handle specific exception types
        import httpx
        if isinstance(e, httpx.TimeoutException):
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Timeout while fetching data from external API"
            )
        elif isinstance(e, httpx.HTTPStatusError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"External API returned error: {e.response.status_code}"
            )
        elif isinstance(e, httpx.RequestError):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to connect to external API"
            )
        elif isinstance(e, ValueError) and "Empty response" in str(e):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Empty response from external API"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch and store paragraph"
            )