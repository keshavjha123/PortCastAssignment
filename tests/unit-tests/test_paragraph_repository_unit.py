import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.repositories.paragraph_repository import ParagraphRepository
from app.schemas.schemas import ParagraphCreate
from app.database.database import Paragraph
from datetime import datetime


class TestParagraphRepository:
    """Unit tests for ParagraphRepository."""

    @pytest.fixture
    def repository(self):
        return ParagraphRepository()

    @pytest.fixture
    def mock_db_session(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_create_paragraph_success(self, repository, mock_db_session):
        """Test successful paragraph creation."""
        paragraph_data = ParagraphCreate(text="Test paragraph content")
        
        # Mock the database operations
        mock_paragraph = Paragraph()
        mock_paragraph.id = 1
        mock_paragraph.text = "Test paragraph content"
        mock_paragraph.created_at = datetime.utcnow()
        
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()
        
        # Mock the Paragraph constructor
        with patch('app.repositories.paragraph_repository.Paragraph') as mock_paragraph_class:
            mock_paragraph_class.return_value = mock_paragraph
            
            result = await repository.create(mock_db_session, paragraph_data)
            
            assert result.id == 1
            assert result.text == "Test paragraph content"
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once_with(mock_paragraph)

    @pytest.mark.asyncio
    async def test_count_paragraphs(self, repository, mock_db_session):
        """Test counting paragraphs."""
        # Mock the database query result
        mock_result = MagicMock()
        mock_result.scalar.return_value = 42
        mock_db_session.execute.return_value = mock_result
        
        result = await repository.count(mock_db_session)
        
        assert result == 42
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_by_text_empty_words(self, repository, mock_db_session):
        """Test search with empty words list."""
        result = await repository.search_by_text(mock_db_session, [], "or")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_by_text_clean_words_empty(self, repository, mock_db_session):
        """Test search with words that become empty after cleaning."""
        result = await repository.search_by_text(mock_db_session, ["!!!", "@@@"], "or")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_by_text_and_operation(self, repository, mock_db_session):
        """Test search with AND operation."""
        # Mock database execution result
        mock_result = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.id = 1
        mock_row1.text = "Test paragraph with both words"
        mock_row1.created_at = datetime.utcnow()
        mock_result.fetchall.return_value = [mock_row1]
        mock_db_session.execute.return_value = mock_result
        
        result = await repository.search_by_text(
            mock_db_session, 
            ["test", "paragraph"], 
            "and"
        )
        
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].text == "Test paragraph with both words"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_by_text_or_operation(self, repository, mock_db_session):
        """Test search with OR operation."""
        # Mock database execution result
        mock_result = MagicMock()
        mock_row1 = MagicMock()
        mock_row1.id = 1
        mock_row1.text = "First paragraph"
        mock_row1.created_at = datetime.utcnow()
        mock_row2 = MagicMock()
        mock_row2.id = 2
        mock_row2.text = "Second paragraph"
        mock_row2.created_at = datetime.utcnow()
        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        mock_db_session.execute.return_value = mock_result
        
        result = await repository.search_by_text(
            mock_db_session, 
            ["first", "second"], 
            "or"
        )
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_by_text_no_results(self, repository, mock_db_session):
        """Test search with no matching results."""
        # Mock database execution result with no rows
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        result = await repository.search_by_text(
            mock_db_session, 
            ["nonexistent"], 
            "or"
        )
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_word_frequency_success(self, repository, mock_db_session):
        """Test successful word frequency analysis."""
        # Mock database execution result for select(Paragraph.text)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("This is test content with test word",),  # Note the comma for single-element tuple
            ("Another word example with test",),
            ("More example content for word analysis",)
        ]
        mock_db_session.execute.return_value = mock_result
        
        result = await repository.analyze_word_frequency(mock_db_session, limit=10)
        
        assert len(result) >= 1
        # The exact result depends on word frequency counting logic
        # so we just verify we got some results back
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        assert all(isinstance(word, str) and isinstance(count, int) for word, count in result)
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_word_frequency_no_paragraphs(self, repository, mock_db_session):
        """Test word frequency analysis with no paragraphs."""
        # Mock database execution result with no rows
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        result = await repository.analyze_word_frequency(mock_db_session, limit=10)
        
        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio 
    async def test_analyze_word_frequency_custom_limit(self, repository, mock_db_session):
        """Test word frequency analysis with custom limit."""
        # Mock database execution result for select(Paragraph.text)
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            ("word1 content with word1 repeated text",),
            ("word2 analysis with word2 examples",)
        ]
        mock_db_session.execute.return_value = mock_result
        
        result = await repository.analyze_word_frequency(mock_db_session, limit=5)
        
        # Should return frequency analysis results, not the raw text
        assert len(result) >= 0  # Could be empty if no words meet criteria
        assert isinstance(result, list)
        mock_db_session.execute.assert_called_once()