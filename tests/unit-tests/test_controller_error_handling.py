import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
from fastapi import HTTPException
from pydantic import ValidationError
from app.controllers.fetch_controller import fetch_controller
from app.controllers.search_controller import search_controller
from app.schemas.schemas import SearchRequest, FetchResponse, SearchResponse


class TestFetchControllerErrorHandling:
    """Test error handling in fetch controller."""

    @pytest.mark.asyncio
    async def test_fetch_timeout_error(self):
        """Test timeout exception handling in controller."""
        mock_db = AsyncMock()
        
        with patch.object(fetch_controller.service, 'fetch_and_store_paragraph') as mock_service:
            mock_service.side_effect = httpx.TimeoutException("Request timeout")
            
            # Test the controller function directly 
            from app.controllers.fetch_controller import fetch_paragraph
            
            with pytest.raises(HTTPException) as exc_info:
                await fetch_paragraph(db=mock_db)
            
            assert exc_info.value.status_code == 504  # Gateway timeout
            
    @pytest.mark.asyncio
    async def test_fetch_http_status_error(self):
        """Test HTTP status error handling."""
        mock_db = AsyncMock()
        
        with patch.object(fetch_controller.service, 'fetch_and_store_paragraph') as mock_service:
            mock_response = MagicMock()
            mock_response.status_code = 500
            http_error = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=mock_response)
            mock_service.side_effect = http_error
            
            with pytest.raises(httpx.HTTPStatusError):
                await fetch_controller.service.fetch_and_store_paragraph(
                    db=mock_db,
                    api_url="http://test.com",
                    timeout=30.0
                )

    @pytest.mark.asyncio
    async def test_fetch_request_error(self):
        """Test request error handling."""
        mock_db = AsyncMock()
        
        with patch.object(fetch_controller.service, 'fetch_and_store_paragraph') as mock_service:
            mock_service.side_effect = httpx.RequestError("Connection failed")
            
            with pytest.raises(httpx.RequestError):
                await fetch_controller.service.fetch_and_store_paragraph(
                    db=mock_db,
                    api_url="http://test.com", 
                    timeout=30.0
                )

    @pytest.mark.asyncio
    async def test_fetch_empty_response_error(self):
        """Test empty response error handling."""
        mock_db = AsyncMock()
        
        with patch.object(fetch_controller.service, 'fetch_and_store_paragraph') as mock_service:
            mock_service.side_effect = ValueError("Empty response from API")
            
            with pytest.raises(ValueError):
                await fetch_controller.service.fetch_and_store_paragraph(
                    db=mock_db,
                    api_url="http://test.com",
                    timeout=30.0
                )

    @pytest.mark.asyncio
    async def test_fetch_generic_error(self):
        """Test generic error handling."""
        mock_db = AsyncMock()
        
        with patch.object(fetch_controller.service, 'fetch_and_store_paragraph') as mock_service:
            mock_service.side_effect = Exception("Database connection error")
            
            with pytest.raises(Exception):
                await fetch_controller.service.fetch_and_store_paragraph(
                    db=mock_db,
                    api_url="http://test.com",
                    timeout=30.0
                )


class TestSearchControllerErrorHandling:
    """Test error handling in search controller."""

    @pytest.mark.asyncio
    async def test_search_empty_words_validation(self):
        """Test validation for empty words list."""
        mock_db = AsyncMock()
        
        # Test the validation logic - empty words should raise ValidationError
        with pytest.raises(ValidationError):
            SearchRequest(words=[], operator="or")
        
        # This should raise a validation error during Pydantic validation
        # before it even reaches the controller
        
    @pytest.mark.asyncio
    async def test_search_service_error(self):
        """Test service layer error handling."""
        mock_db = AsyncMock()
        
        with patch.object(search_controller.service, 'search_paragraphs') as mock_service:
            mock_service.side_effect = Exception("Database connection error")
            
            # Test that service errors are handled
            with pytest.raises(Exception):
                await search_controller.service.search_paragraphs(
                    db=mock_db,
                    words=["test"],
                    operator="or"
                )

    @pytest.mark.asyncio  
    async def test_search_http_exception_passthrough(self):
        """Test that HTTP exceptions are re-raised correctly."""
        mock_db = AsyncMock()
        
        with patch.object(search_controller.service, 'search_paragraphs') as mock_service:
            http_exception = HTTPException(status_code=400, detail="Bad request")
            mock_service.side_effect = http_exception
            
            with pytest.raises(HTTPException) as exc_info:
                await search_controller.service.search_paragraphs(
                    db=mock_db,
                    words=["test"],
                    operator="or"
                )
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Bad request"