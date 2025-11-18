# Secure User Model API (FastAPI, SQLAlchemy, Pydantic, Docker)

This project is a FastAPI application implementing a secure user model with password hashing (bcrypt), Pydantic validation, and a full CI/CD pipeline using GitHub Actions and Docker.

## 🧪 How to Run Tests Locally

### Prerequisites

1.  **Docker:** Must be installed and running.
2.  **Virtual Environment:** Ensure you have activated your Python virtual environment.

### Steps

1.  **Start the Local Database:** Use Docker Compose to start the PostgreSQL container.
    ```bash
    docker-compose up -d db
    ```
2.  **Wait for the DB:** Give the database a moment to fully initialize (check its logs with `docker logs postgres_db`).
3.  **Set Environment Variable:** Set the `TEST_DATABASE_URL` environment variable to point to the local database.
    ```bash
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


