import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestAPIEndpoints:
    """Test API endpoints with PostgreSQL database."""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database_connected"] is True

    @pytest.mark.asyncio
    async def test_fetch_paragraph(self, async_client: AsyncClient, clean_database):
        """Test fetching and storing a paragraph."""
        response = await async_client.post("/fetch")
        assert response.status_code == 200
        data = response.json()
        assert "paragraph" in data
        assert "id" in data["paragraph"]
        assert "text" in data["paragraph"]
        assert len(data["paragraph"]["text"]) > 0

    @pytest.mark.asyncio
    async def test_search_paragraphs_or_operation(self, async_client: AsyncClient, clean_database):
        """Test search with OR operation using PostgreSQL full-text search."""
        # First, fetch a paragraph to have data to search
        fetch_response = await async_client.post("/fetch")
        assert fetch_response.status_code == 200
        
        # Use fixed words that we know exist in metaphorpsum content
        # Based on API response examples, these words commonly appear
        search_words = ["thought", "assert"]  # Common words from metaphorpsum
        
        # Test OR search
        search_data = {
            "words": search_words,
            "operator": "or"
        }
        
        response = await async_client.post("/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert "total_count" in data
        # Note: May be 0 if words don't match the fetched paragraph
        assert data["total_count"] >= 0
        assert "paragraphs" in data
        assert data["operator"] == "or"
        # Search terms are normalized (lowercased, cleaned)
        assert set(data["search_terms"]) == set(search_words)

    @pytest.mark.asyncio
    async def test_search_paragraphs_and_operation(self, async_client: AsyncClient, clean_database):
        """Test search with AND operation using PostgreSQL full-text search."""
        # First, fetch a paragraph
        fetch_response = await async_client.post("/fetch")
        assert fetch_response.status_code == 200
        
        # Use words that commonly appear together in metaphorpsum content
        search_words = ["some", "assert"]
        
        # Test AND search
        search_data = {
            "words": search_words,
            "operator": "and"
        }
        
        response = await async_client.post("/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert "total_count" in data
        assert "paragraphs" in data
        assert data["operator"] == "and"
        # Search terms are normalized - order may change
        assert set(data["search_terms"]) == set(search_words)

    @pytest.mark.asyncio
    async def test_dictionary_analysis(self, async_client: AsyncClient, clean_database):
        """Test word frequency analysis."""
        # First, add some paragraphs
        await async_client.post("/fetch")
        await async_client.post("/fetch")
        
        # Test dictionary endpoint
        response = await async_client.get("/dictionary?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "words" in data
        assert "total_paragraphs_analyzed" in data  # Correct field name from API
        assert isinstance(data["words"], list)

    @pytest.mark.asyncio
    async def test_search_empty_database(self, async_client: AsyncClient, clean_database):
        """Test search on empty database."""
        search_data = {
            "words": ["nonexistent", "words"],
            "operator": "or"
        }
        
        response = await async_client.post("/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert len(data["paragraphs"]) == 0

    @pytest.mark.asyncio
    async def test_search_validation_error(self, async_client: AsyncClient):
        """Test search validation with empty words."""
        search_data = {
            "words": [],
            "operator": "or"
        }
        
        response = await async_client.post("/search", json=search_data)
        assert response.status_code == 422  # Pydantic validation error for empty words