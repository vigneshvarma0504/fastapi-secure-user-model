from fastapi import status
from app.security import verify_password
from app import models, schemas
from sqlalchemy.orm import Session
import pytest

# Use the client and session fixtures from conftest.py

# --- User Registration Tests ---

def test_create_user_success(integration_client, integration_db_session: Session):
    """Test successful user creation via the API and verify data integrity in DB."""
    user_data = {
        "username": "inttestuser1",
        "email": "inttest1@example.com",
        "password": "integrationpassword1"
    }
    
    response = integration_client.post("/users/register", json=user_data)
    
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
    response1 = integration_client.post("/users/register", json=user_data_1)
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Second user creation with same email (should fail)
    response2 = integration_client.post("/users/register", json=user_data_2)
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
    response1 = integration_client.post("/users/register", json=user_data_1)
    assert response1.status_code == status.HTTP_201_CREATED
    
    # Second user creation with same username (should fail)
    response2 = integration_client.post("/users/register", json=user_data_2)
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already taken" in response2.json()["detail"]

def test_register_with_short_password(integration_client):
    """Test that registration fails with password less than 8 characters."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "short"
    }
    
    response = integration_client.post("/users/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_with_invalid_email(integration_client):
    """Test that registration fails with invalid email format."""
    user_data = {
        "username": "testuser",
        "email": "invalidemail",
        "password": "validpassword123"
    }
    
    response = integration_client.post("/users/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# --- User Login Tests ---

def test_login_success(integration_client, integration_db_session: Session):
    """Test successful user login."""
    # First register a user
    user_data = {
        "username": "loginuser",
        "email": "loginuser@example.com",
        "password": "loginpassword123"
    }
    
    reg_response = integration_client.post("/users/register", json=user_data)
    assert reg_response.status_code == status.HTTP_201_CREATED
    
    # Now try to login
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    login_response = integration_client.post("/users/login", json=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    
    user_read = schemas.UserRead(**login_response.json())
    assert user_read.email == user_data["email"]
    assert user_read.username == user_data["username"]

def test_login_invalid_email(integration_client):
    """Test login failure with non-existent email."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "somepassword"
    }
    
    response = integration_client.post("/users/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid email or password" in response.json()["detail"]

def test_login_invalid_password(integration_client):
    """Test login failure with incorrect password."""
    # First register a user
    user_data = {
        "username": "wrongpassworduser",
        "email": "wrongpass@example.com",
        "password": "correctpassword123"
    }
    
    reg_response = integration_client.post("/users/register", json=user_data)
    assert reg_response.status_code == status.HTTP_201_CREATED
    
    # Try to login with wrong password
    login_data = {
        "email": user_data["email"],
        "password": "wrongpassword123"
    }
    
    login_response = integration_client.post("/users/login", json=login_data)
    assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid email or password" in login_response.json()["detail"]


# --- Calculation BREAD Tests ---

def test_add_calculation_success(integration_client, integration_db_session: Session):
    """Test creating a new calculation (Add)."""
    calc_data = {
        "operation": "add",
        "operand_a": 5.0,
        "operand_b": 3.0
    }
    
    response = integration_client.post("/calculations", json=calc_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    calc_read = schemas.CalculationRead(**response.json())
    
    # Verify response structure
    assert calc_read.operation == "add"
    assert calc_read.operand_a == 5.0
    assert calc_read.operand_b == 3.0
    assert calc_read.result == 8.0
    assert calc_read.id is not None
    assert calc_read.user_id == 1
    
    # Verify in database
    db_calc = integration_db_session.query(models.Calculation).filter(
        models.Calculation.id == calc_read.id
    ).first()
    assert db_calc is not None
    assert db_calc.result == 8.0

def test_add_calculation_subtract(integration_client):
    """Test subtract operation."""
    calc_data = {
        "operation": "subtract",
        "operand_a": 10.0,
        "operand_b": 3.0
    }
    
    response = integration_client.post("/calculations", json=calc_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    calc_read = schemas.CalculationRead(**response.json())
    assert calc_read.result == 7.0

def test_add_calculation_multiply(integration_client):
    """Test multiply operation."""
    calc_data = {
        "operation": "multiply",
        "operand_a": 4.0,
        "operand_b": 5.0
    }
    
    response = integration_client.post("/calculations", json=calc_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    calc_read = schemas.CalculationRead(**response.json())
    assert calc_read.result == 20.0

def test_add_calculation_divide(integration_client):
    """Test divide operation."""
    calc_data = {
        "operation": "divide",
        "operand_a": 20.0,
        "operand_b": 4.0
    }
    
    response = integration_client.post("/calculations", json=calc_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    calc_read = schemas.CalculationRead(**response.json())
    assert calc_read.result == 5.0

def test_add_calculation_divide_by_zero(integration_client):
    """Test divide by zero error handling."""
    calc_data = {
        "operation": "divide",
        "operand_a": 10.0,
        "operand_b": 0.0
    }
    
    response = integration_client.post("/calculations", json=calc_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Division by zero" in response.json()["detail"]

def test_browse_calculations(integration_client, integration_db_session: Session):
    """Test retrieving all calculations (Browse)."""
    # Add multiple calculations
    calc_data_1 = {
        "operation": "add",
        "operand_a": 1.0,
        "operand_b": 2.0
    }
    calc_data_2 = {
        "operation": "multiply",
        "operand_a": 3.0,
        "operand_b": 4.0
    }
    
    integration_client.post("/calculations", json=calc_data_1)
    integration_client.post("/calculations", json=calc_data_2)
    
    # Browse calculations
    response = integration_client.get("/calculations")
    
    assert response.status_code == status.HTTP_200_OK
    calculations = response.json()
    assert len(calculations) >= 2
    
    # Verify calculations exist
    operations = [calc["operation"] for calc in calculations]
    assert "add" in operations
    assert "multiply" in operations

def test_read_calculation(integration_client, integration_db_session: Session):
    """Test retrieving a specific calculation (Read)."""
    # First create a calculation
    calc_data = {
        "operation": "add",
        "operand_a": 7.0,
        "operand_b": 2.0
    }
    
    create_response = integration_client.post("/calculations", json=calc_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    calc_id = create_response.json()["id"]
    
    # Now read it
    read_response = integration_client.get(f"/calculations/{calc_id}")
    
    assert read_response.status_code == status.HTTP_200_OK
    calc_read = schemas.CalculationRead(**read_response.json())
    assert calc_read.id == calc_id
    assert calc_read.operation == "add"
    assert calc_read.result == 9.0

def test_read_nonexistent_calculation(integration_client):
    """Test reading a non-existent calculation."""
    response = integration_client.get("/calculations/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Calculation not found" in response.json()["detail"]

def test_edit_calculation(integration_client, integration_db_session: Session):
    """Test updating a calculation (Edit)."""
    # First create a calculation
    calc_data = {
        "operation": "add",
        "operand_a": 5.0,
        "operand_b": 3.0
    }
    
    create_response = integration_client.post("/calculations", json=calc_data)
    calc_id = create_response.json()["id"]
    
    # Update it
    update_data = {
        "operation": "multiply",
        "operand_a": 2.0,
        "operand_b": 3.0
    }
    
    edit_response = integration_client.put(f"/calculations/{calc_id}", json=update_data)
    
    assert edit_response.status_code == status.HTTP_200_OK
    calc_read = schemas.CalculationRead(**edit_response.json())
    assert calc_read.operation == "multiply"
    assert calc_read.operand_a == 2.0
    assert calc_read.operand_b == 3.0
    assert calc_read.result == 6.0

def test_edit_calculation_partial(integration_client):
    """Test partial update of a calculation."""
    # First create a calculation
    calc_data = {
        "operation": "add",
        "operand_a": 5.0,
        "operand_b": 3.0
    }
    
    create_response = integration_client.post("/calculations", json=calc_data)
    calc_id = create_response.json()["id"]
    
    # Partially update it (only update operand_b)
    update_data = {
        "operand_b": 7.0
    }
    
    edit_response = integration_client.put(f"/calculations/{calc_id}", json=update_data)
    
    assert edit_response.status_code == status.HTTP_200_OK
    calc_read = schemas.CalculationRead(**edit_response.json())
    assert calc_read.operation == "add"
    assert calc_read.operand_a == 5.0
    assert calc_read.operand_b == 7.0
    assert calc_read.result == 12.0

def test_edit_nonexistent_calculation(integration_client):
    """Test updating a non-existent calculation."""
    update_data = {
        "operation": "subtract",
        "operand_a": 10.0,
        "operand_b": 5.0
    }
    
    response = integration_client.put("/calculations/99999", json=update_data)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Calculation not found" in response.json()["detail"]

def test_delete_calculation(integration_client, integration_db_session: Session):
    """Test deleting a calculation (Delete)."""
    # First create a calculation
    calc_data = {
        "operation": "add",
        "operand_a": 5.0,
        "operand_b": 3.0
    }
    
    create_response = integration_client.post("/calculations", json=calc_data)
    calc_id = create_response.json()["id"]
    
    # Delete it
    delete_response = integration_client.delete(f"/calculations/{calc_id}")
    
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    get_response = integration_client.get(f"/calculations/{calc_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_nonexistent_calculation(integration_client):
    """Test deleting a non-existent calculation."""
    response = integration_client.delete("/calculations/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Calculation not found" in response.json()["detail"]

def test_calculation_invalid_operation(integration_client):
    """Test creating calculation with invalid operation."""
    calc_data = {
        "operation": "invalid_op",
        "operand_a": 5.0,
        "operand_b": 3.0
    }
    
    response = integration_client.post("/calculations", json=calc_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid operation" in response.json()["detail"]
