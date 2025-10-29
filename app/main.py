import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import init_db, get_db
from app.controllers import fetch_controller, search_controller, dictionary_controller
from app.schemas.schemas import HealthResponse


# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting up the application...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e
    
    yield
    
    # Shutdown
    logger.info("Shutting down the application...")


app = FastAPI(
    title="PortCast Text Analysis API",
    description="A REST API for fetching, storing, and analyzing text paragraphs with full-text search capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(fetch_controller.router, prefix="/fetch", tags=["fetch"])
app.include_router(search_controller.router, prefix="/search", tags=["search"])  
app.include_router(dictionary_controller.router, prefix="/dictionary", tags=["dictionary"])


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to PortCast Text Analysis API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health",
        "endpoints": {
            "fetch": "/fetch - POST: Fetch and store paragraphs from external API",
            "search": "/search - POST: Search stored paragraphs with full-text search",
            "dictionary": "/dictionary - GET: Get most frequent words with definitions"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity."""
    try:
        # Test database connection
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        database_connected = True
        logger.info("Health check passed - database connected")
    except Exception as e:
        database_connected = False
        logger.error(f"Health check failed - database error: {e}")
    
    return HealthResponse(
        status="healthy" if database_connected else "unhealthy",
        timestamp=datetime.utcnow(),
        database_connected=database_connected
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    """Custom 500 handler."""
    from fastapi.responses import JSONResponse
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )