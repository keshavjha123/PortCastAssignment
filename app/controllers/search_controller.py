import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.schemas import SearchRequest, SearchResponse
from app.services.paragraph_service import ParagraphService


logger = logging.getLogger(__name__)
router = APIRouter()


class SearchController:
    """Controller for paragraph search operations."""
    
    def __init__(self):
        self.service = ParagraphService()


search_controller = SearchController()


@router.post("", response_model=SearchResponse)
async def search_paragraphs(
    search_request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    # AI assisted definition of the route.
    
    Search stored paragraphs using full-text search with PostgreSQL.
    
    Args:
        search_request: SearchRequest containing words list and operator ('and' or 'or')
        db: Database session
        
    Returns:
        SearchResponse: Matching paragraphs with search metadata
        
    Raises:
        HTTPException: If database error occurs or invalid search parameters
    """
    try:
        # Validate search request
        if not search_request.words:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one search word must be provided"
            )
        
        # Perform the search using service layer
        matching_paragraphs = await search_controller.service.search_paragraphs(
            db=db,
            words=search_request.words,
            operator=search_request.operator
        )
        
        total_count = len(matching_paragraphs)
        
        return SearchResponse(
            paragraphs=matching_paragraphs,
            total_count=total_count,
            search_terms=search_request.words,
            operator=search_request.operator
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search_paragraphs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during search"
        )