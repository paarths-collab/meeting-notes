"""
Database Session Management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.database import Base

# Database URL - uses environment variable or Docker default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://meetinguser:meetingpass@localhost:5434/meetings"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
