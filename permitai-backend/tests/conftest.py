import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set testing environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "testsecret-9a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
os.environ["CLAUDE_API_KEY"] = "mock"
os.environ["SENDGRID_API_KEY"] = "mock"
os.environ["AWS_ACCESS_KEY_ID"] = "mock"

from app.main import app
from app.database.db import Base
from app.database.session import get_db
from app.tasks.celery_app import celery_app

# Enable synchronous eager execution for Celery tasks in tests
celery_app.conf.task_always_eager = True

# Create testing engine
engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except PermissionError:
            pass

@pytest.fixture
def db():
    # Recreate tables to ensure a clean state for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
