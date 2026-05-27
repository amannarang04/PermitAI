from sqlalchemy.orm import sessionmaker
from typing import Generator
from app.database.db import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """FastAPI dependency to yield a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
