from fastapi import status
from app.security import verify_password
from app import models, schemas
from sqlalchemy.orm import Session
import pytest

# Use the client and session fixtures from conftest.py

def test_create_user_success(integration_client, integration_db_session: Session):
    """Test successful user creation via the API and verify data integrity in DB."""
    user_data = {
        "username": "inttestuser1",
        "email": "inttest1@example.com",
        "password": "integrationpassword1"
    }
    
    response = integration_client.post("/users/", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    user_read = schemas.UserRead(**response.json())
    
    # 1. Verify response structure (UserRead schema)
    assert user_read.email == user_data["email"]
    assert "password_hash" not in response.json() 
    assert user_read.id is not None
    
    # 2. Verify data in the database
    db_user = integration_db_session.query(models.User).filter(models.User.id == user_read.id).first()
    assert db_user is not None
    assert db_user.username == user_data["username"]
    
    # 3. Verify password hash
    assert verify_password(user_data["password"], db_user.password_hash) is True
    
def test_create_user_duplicate_email(integration_client, integration_db_session: Session):
    """Test failure when trying to register a user with a duplicate email."""
    user_data_1 = {
        "username": "inttestuser2",
        "email": "duplicate@example.com",
        "password": "password1"
    }
    user_data_2 = {
        "username": "inttestuser3",
        "email": "duplicate@example.com",
        "password": "password2"
    }
    
    # First user creation (should succeed)
    response1 = integration_client.post("/users/", json=user_data_1)
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Second user creation with same email (should fail)
    response2 = integration_client.post("/users/", json=user_data_2)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response2.json()["detail"]

def test_create_user_duplicate_username(integration_client, integration_db_session: Session):
    """Test failure when trying to register a user with a duplicate username."""
    user_data_1 = {
        "username": "duplicate_name",
        "email": "unique1@example.com",
        "password": "password1"
    }
    user_data_2 = {
        "username": "duplicate_name",
        "email": "unique2@example.com",
        "password": "password2"
    }
    
    # First user creation (should succeed)
    response1 = integration_client.post("/users/", json=user_data_1)
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Second user creation with same username (should fail)
    response2 = integration_client.post("/users/", json=user_data_2)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already taken" in response2.json()["detail"]
