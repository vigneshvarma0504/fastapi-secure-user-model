from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get DB connection URL from environment variables
# In local dev, this loads from .env. In tests, it uses the exported URL.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fastapi_db")

# Setup engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for getting a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
