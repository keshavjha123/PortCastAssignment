# PortCast Text Analysis API

A high-performance REST API for fetching, storing, and analyzing text paragraphs with full-text search capabilities using FastAPI, PostgreSQL, and async/await patterns.

### Viewing the Application

You can explore the API documentation interactively or access the deployed frontend:

- **API Docs**: Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the Swagger UI.
- **Web Frontend**: Access the live client at [https://port-cast-front-end.vercel.app/](https://port-cast-front-end.vercel.app/)

## 🏗️ System Architecture

### Technology Stack
- **Backend**: FastAPI with Python 3.11
- **Database**: PostgreSQL 15 with full-text search (TSVECTOR, GIN indexes)
- **ORM**: SQLAlchemy 2.0 with async support
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest with async support and coverage reporting
- **External APIs**: Metaphorpsum (paragraph generation), Dictionary API

### Key Features
- ⚡ **High Concurrency**: Full async/await implementation
- 🔍 **Advanced Search**: PostgreSQL full-text search with AND/OR operations
- 📊 **Word Analysis**: Frequency analysis with stop-word filtering
- 🐳 **Containerized**: Docker-based deployment
- 🧪 **Comprehensive Testing**: 73 tests with 90% coverage (unit, integration, and E2E tests)
- 📚 **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 📁 Project Structure

```
PortCastAssignment/
├── app/                           # Application source code
│   ├── controllers/               # API route handlers
│   │   ├── search_controller.py   # Search endpoints
│   │   ├── fetch_controller.py    # Paragraph fetching
│   │   └── dictionary_controller.py # Word frequency analysis
│   ├── services/                  # Business logic layer
│   │   ├── paragraph_service.py   # Core paragraph operations
│   │   └── dictionary_service.py  # Word analysis logic
│   ├── repositories/              # Data access layer
│   │   ├── paragraph_repository.py # Database operations
│   │   └── paragraph_repository_interface.py # Repository contract
│   ├── schemas/                   # Pydantic models
│   │   └── schemas.py            # Request/response models
│   ├── database/                  # Database configuration
│   │   └── database.py           # SQLAlchemy setup & models
│   └── main.py                   # FastAPI application entry point
├── tests/                        # Test suite (73 tests, 90% coverage)
│   ├── conftest.py              # Shared test configuration & fixtures
│   ├── README.md               # Test suite documentation
│   ├── unit-tests/             # Unit tests (54 tests - fast, isolated)
│   │   ├── README.md           # Unit test documentation
│   │   ├── test_app_coverage.py # App error handlers & startup tests
│   │   ├── test_controller_error_handling.py # Controller error scenarios
│   │   ├── test_dictionary_service_unit.py # Dictionary service unit tests
│   │   ├── test_error_handlers.py # Custom error handler tests
│   │   ├── test_paragraph_controller_unit.py # Controller unit tests
│   │   ├── test_paragraph_repository_unit.py # Repository layer tests
│   │   └── test_paragraph_service_unit.py # Service layer unit tests
│   └── end-to-end-tests/       # Integration tests (19 tests - real DB)
│       ├── README.md           # E2E test documentation
│       ├── test_api_postgresql.py # Complete API workflow tests
│       └── test_integration_coverage.py # Error handling integration tests
├── docker-compose.yml           # Multi-container orchestration
├── Dockerfile                   # API container definition
├── requirements.txt             # Python dependencies
├── pytest.ini                  # Test configuration
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd PortCastAssignment
```

### 2. Start with Docker (Recommended)
```bash
# Start all services
docker-compose up -d --build

# Verify services are running
docker-compose ps

# Check API health
curl http://localhost:8000/health
```

### 3. Verify Installation

#### Check Services Status
```bash
# Verify both containers are running
docker-compose ps

# Expected output:
# NAME                     IMAGE                      STATUS
# portcastassignment-api-1 portcastassignment-api     Up
# portcastassignment-db-1  postgres:15               Up
```

#### Test API Endpoints
```bash
# 1. Health check (should return {"status": "healthy"})
curl http://localhost:8000/health

# 2. API Documentation (opens in browser)
# Linux/Mac: open http://localhost:8000/docs
# Windows: Start-Process "http://localhost:8000/docs"

# 3. Test basic functionality
curl -X POST http://localhost:8000/fetch
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"words": ["example"], "operator": "or"}'
```

### 4. Available Endpoints
- **📚 API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **❤️ Health Check**: `GET /health` (Service status)
- **📝 Fetch Paragraph**: `POST /fetch` (Get and store new paragraph)
- **🔍 Search Paragraphs**: `POST /search` (Full-text search with AND/OR)
- **📊 Word Frequency**: `GET /dictionary` (Analyze word frequencies)

## 🧪 Running Tests

The project includes **73 comprehensive tests achieving 90% code coverage**, organized into unit and end-to-end test categories.

### 📊 Test Statistics
- **Total Tests**: 73 (all passing)
- **Coverage**: 90% overall
- **Unit Tests**: 54 tests (fast, isolated components)
- **End-to-End Tests**: 19 tests (complete workflows with real database)

### 🏗️ Test Organization
```
tests/
├── unit-tests/          # 54 unit tests (fast execution)
│   ├── Controllers      # API endpoint error handling
│   ├── Services         # Business logic testing  
│   ├── Repositories     # Data access layer
│   └── App Components   # Error handlers, startup, configuration
└── end-to-end-tests/   # 19 integration tests (real PostgreSQL DB)
    ├── API Workflows    # Complete request-response cycles
    └── Error Integration # Cross-component error handling
```

### 🚀 Prerequisites for Testing
Before running tests, ensure the application is running:

```bash
# 1. Start the application stack (required for E2E tests)
docker-compose up -d --build

# 2. Verify services are running
docker-compose ps

# 3. Check API health (should return {"status": "healthy"})
curl http://localhost:8000/health
```

### 🧪 Running Tests - Complete Guide

#### **1. Run All Tests (Recommended)**
```bash
# Complete test suite with coverage report
docker-compose exec api sh -c "cd /app && python -m pytest --cov=app --cov-report=term-missing tests/ -v"

# Quick run without coverage (faster)
docker-compose exec api sh -c "cd /app && python -m pytest tests/ -v"

# Generate HTML coverage report (opens in browser)
docker-compose exec api sh -c "cd /app && python -m pytest --cov=app --cov-report=html tests/"
```

#### **2. Run Tests by Category**
```bash
# Unit tests only (54 tests - fast, ~1 second)
docker-compose exec api sh -c "cd /app && python -m pytest tests/unit-tests/ -v"

# End-to-end tests only (19 tests - slower, ~10 seconds)
docker-compose exec api sh -c "cd /app && python -m pytest tests/end-to-end-tests/ -v"

# Unit tests with coverage
docker-compose exec api sh -c "cd /app && python -m pytest --cov=app tests/unit-tests/ -v"
```

#### **3. Run Specific Test Files**
```bash
# API endpoint tests (complete workflows)
docker-compose exec api sh -c "cd /app && python -m pytest tests/end-to-end-tests/test_api_postgresql.py -v"

# Service layer tests
docker-compose exec api sh -c "cd /app && python -m pytest tests/unit-tests/test_paragraph_service_unit.py -v"

# Dictionary service tests
docker-compose exec api sh -c "cd /app && python -m pytest tests/unit-tests/test_dictionary_service_unit.py -v"

# Error handling tests
docker-compose exec api sh -c "cd /app && python -m pytest tests/unit-tests/test_controller_error_handling.py -v"
```

#### **4. Run Specific Test Functions**
```bash
# Test specific API endpoint
docker-compose exec api sh -c "cd /app && python -m pytest tests/end-to-end-tests/test_api_postgresql.py::TestAPIEndpoints::test_search_paragraphs_or_operation -v"

# Test specific service function
docker-compose exec api sh -c "cd /app && python -m pytest tests/unit-tests/test_paragraph_service_unit.py::TestParagraphService::test_fetch_and_store_paragraph_success -v"

# Test error scenarios
docker-compose exec api sh -c "cd /app && python -m pytest tests/unit-tests/test_controller_error_handling.py::TestFetchControllerErrorHandling::test_fetch_timeout_error -v"
```

#### **5. Coverage Analysis**
```bash
# Detailed coverage with missing lines
docker-compose exec api sh -c "cd /app && python -m pytest --cov=app --cov-report=term-missing --cov-report=html tests/"

# Coverage for specific modules
docker-compose exec api sh -c "cd /app && python -m pytest --cov=app.services --cov-report=term-missing tests/unit-tests/ -v"

# Fail if coverage below 90%
docker-compose exec api sh -c "cd /app && python -m pytest --cov=app --cov-fail-under=90 tests/"
```

### 🔧 Test Configuration

#### Coverage Settings (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov-fail-under=90
    --cov-report=term-missing
    --cov-report=html:htmlcov
    -v
    --tb=short
asyncio_mode = auto
```

#### Test Database Setup
- **End-to-End Tests**: Use PostgreSQL test database (`portcast_test`)
- **Unit Tests**: Use mocked database connections
- **Automatic Cleanup**: Test database is reset between test runs
- **Isolation**: Each test runs in isolated transaction

### 🔍 Understanding Test Output

#### Success Example:
```bash
========================== 73 passed, 6 warnings ==========================
Coverage: 90% (424 statements, 42 missing)

# Test breakdown:
tests/unit-tests/             54 passed    # Unit tests
tests/end-to-end-tests/       19 passed    # E2E tests
```

#### Coverage Report:
```bash
Name                                    Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
app/controllers/fetch_controller.py        32      1    97%   45
app/controllers/search_controller.py       25      4    84%   46, 58-60, 69
app/database/database.py                   37      0   100%
app/services/paragraph_service.py          41      4    90%   55, 71-73
--------------------------------------------------------------------
TOTAL                                     424     42    90%
```

### 🐛 Troubleshooting Tests

#### If Tests Fail:
```bash
# Check if application is running
docker-compose ps

# Restart services
docker-compose down && docker-compose up -d --build

# Check database connectivity
docker-compose exec api sh -c "cd /app && python -c 'from app.database.database import test_db_connection; import asyncio; asyncio.run(test_db_connection())'"

# Run tests with more verbose output
docker-compose exec api sh -c "cd /app && python -m pytest tests/ -vvs --tb=long"
```

#### Common Issues:
1. **Database not ready**: Wait a few seconds after `docker-compose up`
2. **Port conflicts**: Ensure ports 8000 and 5432 are available
3. **Permission errors**: Run `docker-compose down -v` to clean volumes

### ✅ What the Tests Validate

#### Unit Tests (54 tests) verify:
- **Service Layer Logic**: Paragraph processing, word frequency analysis
- **Repository Operations**: Database queries, search functionality
- **Controller Behavior**: HTTP request handling, error responses
- **Error Scenarios**: Timeout handling, validation errors, API failures
- **Application Setup**: Configuration, middleware, error handlers

#### End-to-End Tests (19 tests) validate:
- **Complete API Workflows**: Fetch → Store → Search → Analyze
- **Database Integration**: PostgreSQL full-text search functionality
- **External API Integration**: Metaphorpsum and Dictionary API interactions
- **Error Propagation**: End-to-end error handling across all layers
- **Performance**: Async/await patterns and concurrent request handling

#### Coverage Areas (90% overall):
- **Controllers**: 84-100% (error handling, request validation)
- **Services**: 83-90% (business logic, external API calls)
- **Repositories**: 99% (database operations, search queries)
- **Database Layer**: 100% (connection handling, migrations)
- **Schemas**: 96% (data validation, serialization)

## 🔧 Development Setup

### Local Development (without Docker)

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Setup PostgreSQL**
```bash
# Start PostgreSQL (adjust connection details in .env)
createdb portcast_api
```

3. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Run Application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables
```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/portcast_api
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/portcast_test

# External API URLs
METAPHORPSUM_URL=http://metaphorpsum.com/paragraphs/1/50
DICTIONARY_API_URL=https://api.dictionaryapi.dev/api/v2/entries/en

# Application Settings
LOG_LEVEL=INFO
DEBUG=false
HTTP_TIMEOUT=30.0

# Docker Configuration (automatically set in docker-compose)
POSTGRES_DB=portcast_api
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
```

### Required Files
Ensure these files exist in your project root:
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - API container definition  
- `requirements.txt` - Python dependencies
- `pytest.ini` - Test configuration

## 🔍 API Usage Examples

### Fetch a Paragraph
```bash
curl -X POST "http://localhost:8000/fetch" \
  -H "Content-Type: application/json"
```

### Search with OR Operation
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "words": ["example", "text"],
    "operator": "or"
  }'
```

### Search with AND Operation
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "words": ["example", "text"],
    "operator": "and"
  }'
```

### Get Word Frequency Analysis
```bash
curl "http://localhost:8000/dictionary?limit=10"
```

## 🗄️ Database Schema

### Paragraphs Table
```sql
CREATE TABLE paragraphs (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', text)) STORED
);

-- Full-text search index
CREATE INDEX idx_paragraphs_search_vector ON paragraphs USING GIN (search_vector);
```

## 🐳 Docker Configuration

### Services
- **api**: FastAPI application (port 8000)
- **db**: PostgreSQL 15 (port 5432)

### Volumes
- `postgres_data`: Persistent database storage

### Health Checks
- API: `curl -f http://localhost:8000/health`
- Database: `pg_isready -U postgres`

## 🧹 Maintenance

### Clean Up Docker Environment
```bash
# Remove containers and volumes (fresh start)
docker-compose down -v --remove-orphans

# Remove unused images
docker image prune -f

# Start fresh
docker-compose up -d --build
```

### Database Reset
```bash
# Connect to database and reset
docker exec -it portcastassignment-db-1 psql -U postgres -d portcast_api -c "TRUNCATE TABLE paragraphs RESTART IDENTITY;"
```

## 📊 Performance Features

### Async/Await Implementation
- **Database Operations**: AsyncSession with asyncpg driver
- **HTTP Requests**: httpx for async external API calls
- **Concurrent Processing**: Full async request handling
- **High Throughput**: Supports concurrent paragraph fetching and analysis

### Search Optimization
- **Full-Text Search**: PostgreSQL TSVECTOR with GIN indexes
- **Query Types**: Support for AND/OR operations with proper ranking
- **Relevance Ranking**: ts_rank scoring for search results
- **Efficient Indexing**: Automatic search vector generation with triggers

### Caching Strategy
- **Connection Pooling**: SQLAlchemy async engine with connection pools
- **Query Optimization**: Efficient search queries with proper indexing
- **Database Performance**: Optimized PostgreSQL configuration for text search

## 🧪 Quality Assurance

### Test Coverage Metrics
- **Overall Coverage**: 90% (424 statements tested)
- **Test Count**: 73 comprehensive tests
- **Pass Rate**: 100% (all tests passing)
- **Test Categories**: Unit (54), Integration (19)

### Code Quality Features
- **Type Safety**: Full type hints with mypy compatibility
- **Error Handling**: Comprehensive exception management
- **Validation**: Pydantic models for request/response validation
- **Logging**: Structured logging with configurable levels
- **Health Monitoring**: Built-in health check endpoints



## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Setup Issues

#### Services Won't Start
```bash
# Check for port conflicts
netstat -an | findstr :8000
netstat -an | findstr :5432

# Clean restart
docker-compose down -v --remove-orphans
docker-compose up -d --build
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Test database connectivity
docker-compose exec db psql -U postgres -d portcast_api -c "SELECT 1;"
```

#### API Not Responding
```bash
# Check API logs
docker-compose logs api

# Restart API service only
docker-compose restart api

# Force rebuild
docker-compose up -d --build --force-recreate api
```

#### Tests Failing
```bash
# Ensure services are running first
docker-compose up -d

# Wait for database to be ready
sleep 10

# Run health check
curl http://localhost:8000/health

# Then run tests
docker-compose exec api sh -c "cd /app && python -m pytest tests/ -v"
```

### Getting Help
- **📚 API Docs**: http://localhost:8000/docs (Interactive documentation)
- **🔍 Logs**: `docker-compose logs api` (Application logs)
- **🗄️ Database**: `docker-compose logs db` (Database logs)
- **🧪 Test Issues**: Check the tests/README.md for detailed test documentation

---

**Quick Start Summary**: `docker-compose up -d --build` → Wait 30 seconds → `curl http://localhost:8000/health` → Visit http://localhost:8000/docs


## 🤖 AI Assistance vs. Personal Contribution

### Where AI Was Utilized
- **Technology Choices**: Used AI to evaluate database options (initially considered Elasticsearch, but identified PostgreSQL as a suitable solution for full-text search after further research).
- **Framework Selection**: Leveraged AI to compare FastAPI and Flask, ultimately choosing FastAPI for its async capabilities and performance benefits.
- **Function Definitions & Paraphrasing**: Employed AI for code structure and paraphrasing throughout the project.
- **Testing**: Used AI to improve test coverage.
- **Documentation**: Refactored files such as `README.md` with AI assistance, followed by manual review and validation.

### Where My Own Decisions and Workflow Were Key
- **Final Technology Decisions**: Personally made the final choices regarding framework and database, considering project requirements and potential limitations.
- **API Development**: Designed and implemented API endpoints, request/response schemas, and DTOs.
- **DevOps & Deployment**: Set up Docker Hub integration and managed cloud deployment.
- **Frontend Integration**: Conducted manual frontend checks to ensure API usability for evaluators.
- **Manual Testing**: Performed hands-on testing of all API endpoints to validate functionality and reliability.
- **Deployment**: Deployed backend on Render (free tier), utilizing Aiven for managed PostgreSQL storage.
- **Frontend**: The client application is deployed on Vercel, fully integrated with all backend API endpoints.

