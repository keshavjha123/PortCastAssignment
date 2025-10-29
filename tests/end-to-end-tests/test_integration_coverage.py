import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import httpx


class TestFetchControllerIntegration:
    """Integration tests for fetch controller error paths."""

    @pytest.mark.asyncio
    async def test_fetch_with_timeout_error(self, async_client: AsyncClient):
        """Test fetch endpoint with timeout error."""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock timeout exception
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.TimeoutException("Timeout")
            
            response = await async_client.post("/fetch")
            assert response.status_code == 504
            assert "timeout" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_fetch_with_http_error(self, async_client: AsyncClient):
        """Test fetch endpoint with HTTP error."""
        # Patch the service method directly to simulate HTTP error
        with patch('app.services.paragraph_service.ParagraphService.fetch_and_store_paragraph') as mock_service:
            mock_service.side_effect = httpx.HTTPStatusError(
                "Service Unavailable",
                request=AsyncMock(),
                response=AsyncMock(status_code=503)
            )

            response = await async_client.post("/fetch")
            # The controller catches HTTPStatusError and returns 502
            assert response.status_code == 502
            assert "external api" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_fetch_with_connection_error(self, async_client: AsyncClient):
        """Test fetch endpoint with connection error."""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection failed")
            
            response = await async_client.post("/fetch")
            assert response.status_code == 503
            assert "unable to connect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_fetch_with_empty_response(self, async_client: AsyncClient):
        """Test fetch endpoint with empty response."""
        with patch('app.services.paragraph_service.ParagraphService.fetch_and_store_paragraph') as mock_service:
            mock_service.side_effect = ValueError("Empty response from external API")
            
            response = await async_client.post("/fetch")
            assert response.status_code == 502
            assert "empty response" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_fetch_with_database_error(self, async_client: AsyncClient):
        """Test fetch endpoint with database error."""
        with patch('app.services.paragraph_service.ParagraphService.fetch_and_store_paragraph') as mock_service:
            mock_service.side_effect = Exception("Database connection failed")
            
            response = await async_client.post("/fetch")
            assert response.status_code == 500
            assert "failed to fetch" in response.json()["detail"].lower()


class TestSearchControllerIntegration:
    """Integration tests for search controller error paths."""

    @pytest.mark.asyncio
    async def test_search_with_service_error(self, async_client: AsyncClient):
        """Test search endpoint with service error."""
        with patch('app.services.paragraph_service.ParagraphService.search_paragraphs') as mock_service:
            mock_service.side_effect = Exception("Database query failed")
            
            search_data = {
                "words": ["test"],
                "operator": "or"
            }
            
            response = await async_client.post("/search", json=search_data)
            assert response.status_code == 500
            assert "unexpected error" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_search_validation_error_handling(self, async_client: AsyncClient):
        """Test search endpoint validation."""
        # Test with invalid operator
        search_data = {
            "words": ["test"],
            "operator": "invalid"
        }
        
        response = await async_client.post("/search", json=search_data)
        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_search_missing_fields(self, async_client: AsyncClient):
        """Test search with missing required fields."""
        # Missing operator
        search_data = {
            "words": ["test"]
        }
        
        response = await async_client.post("/search", json=search_data)
        assert response.status_code == 422


class TestHealthCheckEdgeCases:
    """Test health check edge cases."""

    @pytest.mark.asyncio
    async def test_health_check_database_failure(self, async_client: AsyncClient):
        """Test health check when database is down."""
        # Patch the get_db dependency at the app level
        from app.main import app
        from app.database.database import get_db
        
        # Create a mock session that fails on execute
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database connection failed")

        async def failing_db():
            yield mock_session

        # Override the dependency for this test
        app.dependency_overrides[get_db] = failing_db
        
        try:
            response = await async_client.get("/health")
            assert response.status_code == 200  # Health endpoint always returns 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database_connected"] == False
        finally:
            # Clean up the override
            app.dependency_overrides = {}
            assert data["database_connected"] is False


class TestDictionaryControllerIntegration:
    """Integration tests for dictionary controller error paths."""

    @pytest.mark.asyncio
    async def test_dictionary_with_service_error(self, async_client: AsyncClient):
        """Test dictionary endpoint with service error."""
        with patch('app.services.dictionary_service.DictionaryService.analyze_word_frequency_with_definitions') as mock_service:
            mock_service.side_effect = Exception("Dictionary API failed")
            
            response = await async_client.get("/dictionary")
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_dictionary_with_invalid_limit(self, async_client: AsyncClient):
        """Test dictionary endpoint with invalid limit parameter."""
        response = await async_client.get("/dictionary?limit=-1")
        # Should handle validation or convert to valid value
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_dictionary_with_no_data(self, async_client: AsyncClient, clean_database):
        """Test dictionary endpoint with no paragraphs in database."""
        response = await async_client.get("/dictionary")
        assert response.status_code == 200
        data = response.json()
        assert "words" in data
        # Should handle empty database gracefully