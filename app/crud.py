from sqlalchemy.orm import Session
from app import models, schemas
from app.security import hash_password, verify_password

# --- User CRUD ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Hash the raw password before storing
    hashed_password = hash_password(user.password)
    db_user = models.User(
        username=user.username, 
        email=user.email, 
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# --- Calculation CRUD ---

def get_calculations(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all calculations for a user (Browse)."""
    return db.query(models.Calculation).filter(
        models.Calculation.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_calculation(db: Session, calculation_id: int, user_id: int):
    """Get a specific calculation (Read)."""
    return db.query(models.Calculation).filter(
        models.Calculation.id == calculation_id,
        models.Calculation.user_id == user_id
    ).first()


def create_calculation(db: Session, calculation: schemas.CalculationCreate, user_id: int):
    """Create a new calculation (Add)."""
    # Calculate result based on operation
    result = perform_calculation(
        calculation.operation,
        calculation.operand_a,
        calculation.operand_b
    )
    
    db_calculation = models.Calculation(
        user_id=user_id,
        operation=calculation.operation,
        operand_a=calculation.operand_a,
        operand_b=calculation.operand_b,
        result=result
    )
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


def update_calculation(db: Session, calculation_id: int, user_id: int, 
                      calculation_update: schemas.CalculationUpdate):
    """Update a calculation (Edit)."""
    db_calculation = get_calculation(db, calculation_id, user_id)
    if not db_calculation:
        return None
    
    # Update fields if provided
    update_data = calculation_update.dict(exclude_unset=True)
    
    # If operation or operands changed, recalculate result
    if any(key in update_data for key in ["operation", "operand_a", "operand_b"]):
        operation = update_data.get("operation", db_calculation.operation)
        operand_a = update_data.get("operand_a", db_calculation.operand_a)
        operand_b = update_data.get("operand_b", db_calculation.operand_b)
        
        result = perform_calculation(operation, operand_a, operand_b)
        db_calculation.result = result
    
    for field, value in update_data.items():
        setattr(db_calculation, field, value)
    
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


def delete_calculation(db: Session, calculation_id: int, user_id: int):
    """Delete a calculation (Delete)."""
    db_calculation = get_calculation(db, calculation_id, user_id)
    if db_calculation:
        db.delete(db_calculation)
        db.commit()
        return True
    return False


def perform_calculation(operation: str, operand_a: float, operand_b: float) -> float:
    """Perform the calculation based on operation type."""
    operation = operation.lower()
    
    if operation == "add":
        return operand_a + operand_b
    elif operation == "subtract":
        return operand_a - operand_b
    elif operation == "multiply":
        return operand_a * operand_b
    elif operation == "divide":
        if operand_b == 0:
            raise ValueError("Division by zero")
        return operand_a / operand_b
    else:
        raise ValueError(f"Invalid operation: {operation}")
