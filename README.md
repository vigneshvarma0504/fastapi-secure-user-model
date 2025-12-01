# Secure User Model API - FastAPI

A comprehensive FastAPI application that implements secure user management with authentication, password hashing, and calculation CRUD operations. This project includes full integration testing, Docker containerization, and CI/CD pipeline integration with GitHub Actions and Docker Hub.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Running with Docker](#running-with-docker)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [GitHub Actions CI/CD](#github-actions-cicd)
- [Docker Hub](#docker-hub)
- [Troubleshooting](#troubleshooting)

## Features

### User Management
- **User Registration** (`POST /users/register`): Create new user accounts with secure password hashing using bcrypt
- **User Login** (`POST /users/login`): Authenticate users with email and password verification
- **Secure Password Handling**: Passwords are hashed using bcrypt and never stored in plain text
- **Email Validation**: Built-in email format validation using Pydantic's EmailStr
- **Duplicate Prevention**: Prevents duplicate emails and usernames

### Calculation Operations (BREAD)
- **Browse** (`GET /calculations`): List all calculations with pagination support
- **Read** (`GET /calculations/{id}`): Retrieve a specific calculation by ID
- **Edit** (`PUT /calculations/{id}`): Update calculation with recalculation of results
- **Add** (`POST /calculations`): Create new calculations with automatic result computation
- **Delete** (`DELETE /calculations/{id}`): Remove calculations from the database

Supported operations: `add`, `subtract`, `multiply`, `divide` with proper error handling for division by zero.

### Database
- **PostgreSQL Integration**: Persistent data storage with proper schema and relationships
- **SQLAlchemy ORM**: Type-safe database operations
- **Relationship Management**: User-to-Calculation relationships with cascade delete

### Testing & Quality
- **Integration Tests**: Comprehensive pytest suite with 30+ test cases
- **Database Fixtures**: Isolated test database with proper transaction rollback
- **CI/CD Pipeline**: Automated testing on each commit with GitHub Actions
- **Docker Support**: Complete containerization for consistent environments

## Project Structure

```
fastapi_secure_user_model/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and route definitions
│   ├── models.py            # SQLAlchemy ORM models (User, Calculation)
│   ├── schemas.py           # Pydantic schemas for validation
│   ├── crud.py              # Database CRUD operations
│   ├── security.py          # Password hashing and verification
│   ├── database.py          # Database connection and session management
│   └── __pycache__/
├── tests/
│   ├── conftest.py          # pytest fixtures
│   ├── test_integration.py  # Integration tests
│   ├── test_security.py     # Security tests
│   └── __pycache__/
├── .github/
│   └── workflows/
│       └── test-and-deploy.yml  # GitHub Actions workflow
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Multi-container Docker setup
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Prerequisites

- **Python 3.11+**: Required for running the application
- **PostgreSQL 14+**: Database server (can be run in Docker)
- **Docker & Docker Compose**: For containerized deployment
- **Git**: For version control

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vigneshvarma0504/fastapi-secure-user-model.git
cd fastapi-secure-user-model
```

### 2. Create Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create Environment File

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=fastapi_db
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db
```

### 2. Database Setup

If not using Docker, ensure PostgreSQL is running and the database exists:

```bash
psql -U postgres
CREATE USER user WITH PASSWORD 'password';
CREATE DATABASE fastapi_db OWNER user;
```

## Running Locally

### Without Docker

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
uvicorn app.main:app --reload

# Server will be available at: http://localhost:8000
```

### With Docker Compose

```bash
# Build and start containers
docker-compose up --build

# Server will be available at: http://localhost:8000
```

To run in the background:

```bash
docker-compose up -d --build
```

To stop containers:

```bash
docker-compose down
```

## Testing

### Prerequisites for Testing

1. **Docker**: Running and accessible
2. **PostgreSQL Service**: Started with Docker Compose
3. **Virtual Environment**: Activated

### Run All Tests

```bash
# Start the PostgreSQL database first
docker-compose up -d db

# Wait for database to be ready (check: docker logs postgres_db)

# Set the test database URL
export TEST_DATABASE_URL=postgresql://testuser:testpassword@localhost:5432/test_fastapi_db

# Or use postgres defaults from docker-compose
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db

# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test Files

```bash
# Integration tests only
pytest tests/test_integration.py -v

# Security tests only
pytest tests/test_security.py -v
```

### Run Specific Test Cases

```bash
# Test user registration
pytest tests/test_integration.py::test_create_user_success -v

# Test calculation endpoints
pytest tests/test_integration.py::test_add_calculation_success -v

# Test login functionality
pytest tests/test_integration.py::test_login_success -v
```

### Integration Tests with Docker

Tests automatically use PostgreSQL when `TEST_DATABASE_URL` environment variable is set:

```bash
# Setup and run tests
docker-compose up -d db
sleep 3  # Wait for DB to initialize
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db
pytest tests/test_integration.py -v
```

### View Test Coverage

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=html tests/

# Open the HTML report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## API Documentation

### Interactive API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can test endpoints directly in your browser.

### Manual Testing in Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out" button
4. Enter request data
5. Click "Execute" to test the endpoint
6. View the response in the "Response body" section

## API Endpoints

### User Endpoints

#### Register User
```http
POST /users/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}

Response (201 Created):
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-12-01T10:30:00"
}
```

#### Login User
```http
POST /users/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}

Response (200 OK):
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-12-01T10:30:00"
}
```

### Calculation Endpoints

#### Add Calculation (Create)
```http
POST /calculations
Content-Type: application/json

{
  "operation": "add",
  "operand_a": 10.5,
  "operand_b": 5.3
}

Response (201 Created):
{
  "id": 1,
  "user_id": 1,
  "operation": "add",
  "operand_a": 10.5,
  "operand_b": 5.3,
  "result": 15.8,
  "created_at": "2025-12-01T10:35:00",
  "updated_at": "2025-12-01T10:35:00"
}
```

#### Browse Calculations (Read All)
```http
GET /calculations?skip=0&limit=100

Response (200 OK):
[
  {
    "id": 1,
    "user_id": 1,
    "operation": "add",
    "operand_a": 10.5,
    "operand_b": 5.3,
    "result": 15.8,
    "created_at": "2025-12-01T10:35:00",
    "updated_at": "2025-12-01T10:35:00"
  }
]
```

#### Read Calculation
```http
GET /calculations/{id}

Response (200 OK):
{
  "id": 1,
  "user_id": 1,
  "operation": "add",
  "operand_a": 10.5,
  "operand_b": 5.3,
  "result": 15.8,
  "created_at": "2025-12-01T10:35:00",
  "updated_at": "2025-12-01T10:35:00"
}
```

#### Edit Calculation (Update)
```http
PUT /calculations/{id}
Content-Type: application/json

{
  "operation": "multiply",
  "operand_a": 3.0,
  "operand_b": 4.0
}

Response (200 OK):
{
  "id": 1,
  "user_id": 1,
  "operation": "multiply",
  "operand_a": 3.0,
  "operand_b": 4.0,
  "result": 12.0,
  "created_at": "2025-12-01T10:35:00",
  "updated_at": "2025-12-01T11:00:00"
}
```

#### Delete Calculation
```http
DELETE /calculations/{id}

Response (204 No Content)
```

### Supported Operations

| Operation | Example | Result |
|-----------|---------|--------|
| add | 10 + 5 | 15 |
| subtract | 10 - 5 | 5 |
| multiply | 10 * 5 | 50 |
| divide | 10 / 5 | 2 |

## Deployment

### Local Development
```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

### Docker Container
```bash
docker-compose up --build
```

Access at: http://localhost:8000

### Production (with environment variables)
```bash
docker run -e DATABASE_URL=<db_url> \
           -e POSTGRES_USER=<user> \
           -e POSTGRES_PASSWORD=<password> \
           -e POSTGRES_DB=<db> \
           -p 8000:8000 \
           <docker_image_name>
```

## GitHub Actions CI/CD

The project includes automated CI/CD pipeline configured in `.github/workflows/test-and-deploy.yml`.

### Workflow Overview

**File**: `.github/workflows/test-and-deploy.yml`

The workflow performs the following on every push and pull request:

1. **Test Job** (Always runs):
   - Sets up Python 3.11 environment
   - Starts PostgreSQL 15 database service
   - Installs all dependencies from requirements.txt
   - Runs complete pytest suite with verbose output
   - Tests fail if any test case fails

2. **Build & Push Job** (Only on main branch after tests pass):
   - Sets up Docker Buildx for efficient multi-platform builds
   - Authenticates with Docker Hub using stored credentials
   - Builds Docker image with caching optimization
   - Pushes image with two tags:
     - `latest`: For most recent version
     - `<commit-sha>`: For reproducibility

### Setup Instructions

#### 1. Add Docker Hub Credentials

Add your Docker Hub credentials to GitHub repository secrets:

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:
   - **DOCKER_USERNAME**: Your Docker Hub username
   - **DOCKER_PASSWORD**: Your Docker Hub access token (not password)

To generate Docker Hub token:
1. Log in to Docker Hub
2. Go to Account Settings → Security
3. Click "New Access Token"
4. Generate token with read/write permissions
5. Copy and save as `DOCKER_PASSWORD` in GitHub secrets

#### 2. Verify GitHub Actions

1. Push a commit to your repository
2. Go to **Actions** tab in GitHub
3. Click on the workflow run to view logs
4. Verify all tests pass and image is built

### View Workflow Runs

```
https://github.com/vigneshvarma0504/fastapi-secure-user-model/actions
```

Each run shows:
- ✅ Test results
- 📊 Test coverage
- 🐳 Docker build status
- 📤 Docker Hub push status

## Docker Hub

The Docker image is automatically built and pushed to Docker Hub on every successful test completion on the main branch.

### Docker Hub Repository

**URL**: `https://hub.docker.com/r/<your-docker-username>/fastapi-secure-user-model`

### Available Tags

- `latest`: Most recent stable build
- `<commit-sha>`: Specific commit for reproducibility

### Pull and Run Image

```bash
# Pull the latest image
docker pull <docker_username>/fastapi-secure-user-model:latest

# Run the image
docker run -e DATABASE_URL=postgresql://user:password@db:5432/fastapi_db \
           -e POSTGRES_USER=user \
           -e POSTGRES_PASSWORD=password \
           -e POSTGRES_DB=fastapi_db \
           -p 8000:8000 \
           <docker_username>/fastapi-secure-user-model:latest
```

### Run with Docker Compose using Docker Hub Image

Create `docker-compose.prod.yml`:

```yaml
version: '3.7'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"

  app:
    image: <docker_username>/fastapi-secure-user-model:latest
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

Then run:
```bash
docker-compose -f docker-compose.prod.yml up
```

## Troubleshooting

### Database Connection Error
```
Error: could not connect to server: Connection refused
```

**Solution**:
- Ensure PostgreSQL is running: `docker-compose up -d db`
- Wait for database to initialize: `docker logs postgres_db`
- Check DATABASE_URL environment variable is correct
- Verify database user and password

### Port 8000 Already in Use
```
Error: Address already in use
```

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Docker Compose Build Fails
**Solution**:
```bash
# Clean up old images and volumes
docker-compose down --volumes

# Rebuild
docker-compose up --build
```

### Tests Fail with "TEST_DATABASE_URL not set"
**Solution**:
```bash
# Set test database URL
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db

# Or use the docker-compose database
docker-compose up -d db
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/fastapi_db

# Run tests
pytest tests/test_integration.py -v
```

### Module Not Found Errors
**Solution**:
```bash
# Reinstall requirements without cache
pip install --no-cache-dir -r requirements.txt

# Verify virtual environment is activated
which python
```

### GitHub Actions Tests Fail
**Solution**:
1. Check the GitHub Actions logs for error messages
2. Verify all environment variables are set correctly
3. Ensure requirements.txt is up to date
4. Check database service is starting correctly

## Security Best Practices

1. **Password Hashing**: Uses bcrypt with automatic salt generation
2. **Email Validation**: Built-in validation using email-validator library
3. **SQL Injection Prevention**: Uses SQLAlchemy ORM with parameterized queries
4. **Environment Variables**: Sensitive data stored in .env file, never committed to Git
5. **HTTPS Ready**: Application supports HTTPS when deployed behind reverse proxy
6. **Secure Defaults**: No default credentials, all required to be configured

## Development

### Code Style
- Follow PEP 8 standards
- Use type hints for better code clarity
- Keep functions focused and well-documented

### Adding New Features

1. Create database models in `app/models.py`
2. Create Pydantic schemas in `app/schemas.py`
3. Add CRUD operations in `app/crud.py`
4. Implement routes in `app/main.py`
5. Write comprehensive tests in `tests/test_*.py`
6. Update this README with new endpoints

### Running Tests During Development

```bash
# Watch mode for continuous testing (requires pytest-watch)
pip install pytest-watch
ptw tests/

# With coverage
pytest --cov=app --cov-report=html tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues first
- Provide detailed error messages and steps to reproduce

---

**Last Updated**: December 1, 2025  
**Python Version**: 3.11+  
**FastAPI Version**: 0.121.2  
**Database**: PostgreSQL 14+
    export TEST_DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/fastapi_db"
    ```
4.  **Run Pytest:** Execute the tests.
    ```bash
    pytest tests/
    ```
5.  **Clean Up:** Stop the database container.
    ```bash
    docker-compose down
    ```

## 🐳 Docker Hub Link

The Docker image for this application is pushed to Docker Hub upon successful completion of the CI/CD pipeline on the `main` branch.

**Docker Hub Repository:** [LINK TO YOUR DOCKER HUB REPO HERE - e.g., `https://hub.docker.com/r/YOUR_DOCKER_USERNAME/fastapi-secure-app` ]

## 🚀 How to Run the Application Locally (Docker)

1. **Build and Run:**
    ```bash
    docker-compose up --build
    ```
2. **Access:** The application will be available at `http://localhost:8000`. Access the interactive documentation at `http://localhost:8000/docs`.


