import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app
from app import models
import os

# --- Fixture for Unit/Schema Testing (SQLite) ---

@pytest.fixture(scope="session")
def engine():
    # Use SQLite for simple unit/schema tests that don't need Postgres features
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="session")
def setup_db(engine):
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_db, engine):
    # Setup a new connection and session for each test function
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    db = SessionLocal()
    
    # Override get_db dependency for the test client
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    
    yield db
    
    # Clean up: roll back the transaction and close the connection
    transaction.rollback()
    connection.close()
    
# --- Test Client Fixture ---

@pytest.fixture(scope="function")
def client(db_session):
    # Use the test client with the overridden dependency
    return TestClient(app)

# --- Integration Test Fixture (Postgres) ---

@pytest.fixture(scope="session")
def integration_db_session():
    # Use the dedicated environment variable for integration tests (Postgres)
    # This will be set in the GitHub Actions workflow
    db_url = os.getenv("TEST_DATABASE_URL") 
    if not db_url:
        pytest.skip("TEST_DATABASE_URL not set for integration tests.")
        
    integration_engine = create_engine(db_url)
    
    # Ensure tables are created for the integration test database
    models.Base.metadata.create_all(bind=integration_engine)
    
    IntegrationSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=integration_engine)

    def get_integration_db():
        db = IntegrationSessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    # Temporarily override the dependency to point to the real test database
    app.dependency_overrides[get_db] = get_integration_db
    
    yield IntegrationSessionLocal()

    # Clean up: drop all tables after integration tests (careful with this!)
    models.Base.metadata.drop_all(bind=integration_engine)
    app.dependency_overrides.clear() # Clear the override
    
@pytest.fixture(scope="session")
def integration_client():
    # A dedicated client for integration tests
    return TestClient(app)
