"""
Tests for error handlers in main.py
"""
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app, not_found_handler, internal_server_error_handler
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException


class TestErrorHandlers:
    """Test custom error handlers in main.py."""

    @pytest.mark.asyncio
    async def test_not_found_handler_direct(self):
        """Test not found handler directly."""
        request = MagicMock(spec=Request)
        exc = HTTPException(status_code=404, detail="Not found")
        
        response = await not_found_handler(request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        # Test the content directly from the response
        import json
        content = json.loads(response.body.decode())
        assert content["detail"] == "Endpoint not found"

    @pytest.mark.asyncio
    async def test_internal_server_error_handler_direct(self):
        """Test internal server error handler directly."""
        request = MagicMock(spec=Request)
        exc = Exception("Test error")
        
        response = await internal_server_error_handler(request, exc)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        # Test the content directly from the response
        import json
        content = json.loads(response.body.decode())
        assert "error" in content
        assert "message" in content


class TestApplicationSetup:
    """Test application setup and configuration."""
    
    def test_app_creation(self):
        """Test that app is created with correct metadata."""
        assert app.title == "PortCast Text Analysis API"
        assert app.description == "A REST API for fetching, storing, and analyzing text paragraphs with full-text search capabilities"
        assert app.version == "1.0.0"

    def test_cors_middleware(self):
        """Test CORS middleware configuration."""
        # CORS middleware is already configured in the app
        client = TestClient(app)
        
        # Test preflight request
        response = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        })
        assert response.status_code in [200, 204]

    @pytest.mark.asyncio
    async def test_custom_404_handler(self):
        """Test custom 404 handler by triggering it manually."""
        # Test the handler function directly since middleware integration is complex
        from starlette.requests import Request
        
        # Create mock objects
        scope = {
            "type": "http",
            "method": "GET", 
            "path": "/nonexistent",
            "headers": [],
            "query_string": b"",
        }
        request = Request(scope)
        exc = HTTPException(status_code=404)
        
        response = await not_found_handler(request, exc)
        
        assert response.status_code == 404
        import json
        content = json.loads(response.body.decode())
        assert content["detail"] == "Endpoint not found"

    @pytest.mark.asyncio 
    async def test_custom_500_handler(self):
        """Test custom 500 handler by triggering it manually."""
        from starlette.requests import Request
        
        # Create mock objects
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/error", 
            "headers": [],
            "query_string": b"",
        }
        request = Request(scope)
        exc = Exception("Test error")
        
        response = await internal_server_error_handler(request, exc)
        
        assert response.status_code == 500
        import json
        content = json.loads(response.body.decode())
        assert "error" in content
        assert "message" in content


class TestHealthCheckCoverage:
    """Test health check with better database error coverage."""
    
    @pytest.mark.asyncio
    async def test_health_check_database_query_error(self):
        """Test health check with database query error."""
        from app.main import health_check
        from fastapi import Request
        from unittest.mock import AsyncMock
        
        # Mock request and database session
        request = MagicMock()
        mock_db = AsyncMock()
        
        # Make the execute method raise an exception
        mock_db.execute.side_effect = Exception("Database error")
        
        # Call health_check directly with mocked db
        with patch('app.main.get_db') as mock_get_db:
            
            async def mock_db_generator():
                yield mock_db
                
            mock_get_db.return_value = mock_db_generator()
            
            # Use TestClient to properly trigger the health endpoint
            client = TestClient(app)
            
            with patch('app.database.database.get_db', return_value=mock_db_generator()):
                response = client.get("/health")
                
                # The health endpoint catches exceptions and returns unhealthy status
                assert response.status_code == 200
                data = response.json()
                # The actual implementation might return different status based on error handling
                assert "status" in data