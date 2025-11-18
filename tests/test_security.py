import pytest
from app.security import hash_password, verify_password
from app.schemas import UserCreate, UserRead
from pydantic import ValidationError

# --- Unit Tests for Security (Hashing) ---

def test_password_hashing():
    """Test if hashing produces a valid, different hash each time, and verification works."""
    password = "MySecurePassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Hashes should be different due to the random salt
    assert hash1 != hash2
    
    # Verification should pass for both hashes
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
    
    # Verification should fail for a wrong password
    assert verify_password("WrongPassword", hash1) is False

# --- Unit Tests for Pydantic Schemas ---

def test_user_create_schema_valid():
    """Test successful validation of the UserCreate schema."""
    valid_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword123"
    }
    user_create = UserCreate(**valid_data)
    
    assert user_create.username == valid_data["username"]
    assert user_create.email == valid_data["email"]
    assert user_create.password == valid_data["password"]

def test_user_create_schema_invalid_email():
    """Test validation failure for an invalid email format."""
    invalid_data = {
        "username": "testuser",
        "email": "invalid-email", # Missing domain/TLD
        "password": "strongpassword123"
    }
    with pytest.raises(ValidationError):
        UserCreate(**invalid_data)

def test_user_create_schema_password_too_short():
    """Test validation failure for a password shorter than 8 characters."""
    invalid_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "short" # Too short
    }
    with pytest.raises(ValidationError):
        UserCreate(**invalid_data)
