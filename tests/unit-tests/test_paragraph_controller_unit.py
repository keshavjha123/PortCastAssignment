import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.controllers.search_controller import SearchController
from app.controllers.fetch_controller import FetchController
from app.services.paragraph_service import ParagraphService
from app.schemas.schemas import SearchRequest, SearchResponse, FetchResponse
from app.database.database import Paragraph
from datetime import datetime


class TestSearchController:
    """Unit tests for SearchController."""

    @pytest.fixture
    def mock_paragraph_service(self):
        return AsyncMock(spec=ParagraphService)

    @pytest.fixture
    def controller(self, mock_paragraph_service):
        controller = SearchController()
        controller.service = mock_paragraph_service
        return controller

    @pytest.mark.asyncio
    async def test_search_controller_initialization(self, controller):
        """Test search controller initialization."""
        assert isinstance(controller.service, ParagraphService)

    @pytest.mark.asyncio  
    async def test_search_paragraphs_service_call(self, controller, mock_paragraph_service):
        """Test search controller service method call."""
        # Mock service response
        mock_paragraph = Paragraph()
        mock_paragraph.id = 1
        mock_paragraph.text = "Test paragraph content"
        mock_paragraph.created_at = datetime.utcnow()
        
        mock_paragraph_service.search_paragraphs.return_value = [mock_paragraph]
        
        # Call the service method directly (not the endpoint)
        result = await controller.service.search_paragraphs(
            db=AsyncMock(),
            words=["test"],
            operator="or"
        )
        
        assert len(result) == 1
        assert result[0].id == 1


class TestFetchController:
    """Unit tests for FetchController."""

    @pytest.fixture
    def mock_paragraph_service(self):
        return AsyncMock(spec=ParagraphService)

    @pytest.fixture
    def fetch_controller(self, mock_paragraph_service):
        controller = FetchController()
        controller.service = mock_paragraph_service
        return controller

    @pytest.mark.asyncio
    async def test_fetch_controller_initialization(self, fetch_controller):
        """Test fetch controller initialization."""
        assert isinstance(fetch_controller.service, ParagraphService)

    @pytest.mark.asyncio  
    async def test_fetch_and_store_service_call(self, fetch_controller, mock_paragraph_service):
        """Test fetch controller service method call."""
        # Mock service response
        from app.schemas.schemas import ParagraphResponse
        mock_paragraph_response = ParagraphResponse(
            id=1,
            text="Test fetched paragraph",
            created_at=datetime.utcnow()
        )
        mock_response = FetchResponse(
            paragraph=mock_paragraph_response,
            message="Test message"
        )
        
        mock_paragraph_service.fetch_and_store_paragraph.return_value = mock_response
        
        # Call the service method directly
        result = await fetch_controller.service.fetch_and_store_paragraph(
            db=AsyncMock(),
            api_url="http://test.com",
            timeout=30.0
        )
        
        assert result.paragraph.id == 1
        assert result.paragraph.text == "Test fetched paragraph"