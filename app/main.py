from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.database import engine, get_db

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/users/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check for existing user by email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check for existing user by username (Optional, but good practice)
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
