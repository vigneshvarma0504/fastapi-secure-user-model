from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import engine, get_db
from app.security import verify_password

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure User Model API",
    description="API for user management and calculation operations",
    version="1.0.0"
)

# --- User Endpoints ---

@app.post("/users/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check for existing user by email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check for existing user by username
    db_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
        
    return crud.create_user(db=db, user=user)


@app.post("/users/login", response_model=schemas.UserRead)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login a user with email and password."""
    # Find user by email
    db_user = crud.get_user_by_email(db, email=user_login.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_login.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return db_user


# --- Calculation Endpoints (BREAD) ---

@app.get("/calculations", response_model=list[schemas.CalculationRead])
def browse_calculations(db: Session = Depends(get_db), user_id: int = 1, skip: int = 0, limit: int = 100):
    """Browse all calculations for a user (GET /calculations)."""
    # In a real app, user_id would come from authentication token
    calculations = crud.get_calculations(db, user_id=user_id, skip=skip, limit=limit)
    return calculations


@app.get("/calculations/{calculation_id}", response_model=schemas.CalculationRead)
def read_calculation(calculation_id: int, db: Session = Depends(get_db), user_id: int = 1):
    """Read a specific calculation (GET /calculations/{id})."""
    db_calculation = crud.get_calculation(db, calculation_id=calculation_id, user_id=user_id)
    if not db_calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    return db_calculation


@app.post("/calculations", response_model=schemas.CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(calculation: schemas.CalculationCreate, db: Session = Depends(get_db), user_id: int = 1):
    """Add a new calculation (POST /calculations)."""
    try:
        return crud.create_calculation(db=db, calculation=calculation, user_id=user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.put("/calculations/{calculation_id}", response_model=schemas.CalculationRead)
def edit_calculation(calculation_id: int, calculation_update: schemas.CalculationUpdate, 
                    db: Session = Depends(get_db), user_id: int = 1):
    """Edit a calculation (PUT /calculations/{id})."""
    try:
        db_calculation = crud.update_calculation(db, calculation_id, user_id, calculation_update)
        if not db_calculation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calculation not found"
            )
        return db_calculation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.delete("/calculations/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calculation_id: int, db: Session = Depends(get_db), user_id: int = 1):
    """Delete a calculation (DELETE /calculations/{id})."""
    success = crud.delete_calculation(db, calculation_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    return None


# --- Original Endpoints (kept for backward compatibility) ---

@app.post("/users/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user (legacy endpoint)."""
    # Check for existing user by email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check for existing user by username
    db_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
        
    return crud.create_user(db=db, user=user)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Secure User Model API"}
