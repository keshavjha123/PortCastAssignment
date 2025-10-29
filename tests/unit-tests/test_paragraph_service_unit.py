import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.paragraph_service import ParagraphService
from app.repositories.paragraph_repository import ParagraphRepository
from app.schemas.schemas import ParagraphCreate
from datetime import datetime


class TestParagraphService:
    """Unit tests for ParagraphService."""

    @pytest.fixture
    def mock_repository(self):
        return AsyncMock(spec=ParagraphRepository)

    @pytest.fixture
    def service(self, mock_repository):
        service = ParagraphService()
        service.repository = mock_repository
        return service

    @pytest.fixture
    def mock_db_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_fetch_and_store_paragraph_success(self, service, mock_db_session, mock_repository):
        """Test successful paragraph fetching and storing."""
        # Mock external API response
        mock_paragraph_text = "This is a test paragraph for unit testing."
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = mock_paragraph_text
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Mock repository create method
            mock_paragraph = MagicMock()
            mock_paragraph.id = 1
            mock_paragraph.text = mock_paragraph_text
            mock_paragraph.created_at = datetime.utcnow()
            mock_repository.create.return_value = mock_paragraph
            
            result = await service.fetch_and_store_paragraph(
                db=mock_db_session,
                api_url="http://test.com",
                timeout=30.0
            )
            
            # FetchResponse has paragraph field containing the paragraph data
            assert result.paragraph.id == 1
            assert result.paragraph.text == mock_paragraph_text
            mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_and_store_paragraph_api_failure(self, service, mock_db_session):
        """Test handling of external API failure."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with pytest.raises(Exception):
                await service.fetch_and_store_paragraph(mock_db_session)

    @pytest.mark.asyncio
    async def test_search_paragraphs_success(self, service, mock_db_session, mock_repository):
        """Test successful paragraph searching."""
        # Mock search results
        mock_paragraphs = [
            MagicMock(id=1, text="First paragraph", created_at=datetime.utcnow()),
            MagicMock(id=2, text="Second paragraph", created_at=datetime.utcnow())
        ]
        mock_repository.search_by_text.return_value = mock_paragraphs
        
        result = await service.search_paragraphs(
            db=mock_db_session,
            words=["test", "paragraph"],
            operator="or"
        )
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        mock_repository.search_by_text.assert_called_once_with(
            db=mock_db_session, words=["test", "paragraph"], operator="or"
        )

    @pytest.mark.asyncio
    async def test_search_paragraphs_empty_words(self, service, mock_db_session):
        """Test search with empty words list."""
        result = await service.search_paragraphs(
            db=mock_db_session,
            words=[],
            operator="or"
        )
        
        assert result == []

    @pytest.mark.asyncio
    async def test_search_paragraphs_repository_error(self, service, mock_db_session, mock_repository):
        """Test handling of repository errors during search."""
        mock_repository.search_by_text.side_effect = Exception("Database error")
        
        with pytest.raises(Exception) as exc_info:
            await service.search_paragraphs(
                db=mock_db_session,
                words=["test"],
                operator="or"
            )
        
        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_paragraph_count(self, service, mock_db_session, mock_repository):
        """Test getting paragraph count."""
        mock_repository.count.return_value = 42
        
        result = await service.get_paragraph_count(mock_db_session)
        
        assert result == 42
        mock_repository.count.assert_called_once_with(mock_db_session)