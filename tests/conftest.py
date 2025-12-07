# tests/conftest.py
"""
Pytest fixtures for testing.
Uses a temporary file SQLite database to avoid in-memory DB issues.
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base, get_db


# Create a temp file for test database
_temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
TEST_DATABASE_URL = f"sqlite:///{_temp_db_file.name}"

# Create test engine and session
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override the get_db dependency for testing."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables before tests, drop after."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Cleanup after all tests
    Base.metadata.drop_all(bind=test_engine)
    # Remove temp file
    try:
        os.unlink(_temp_db_file.name)
    except OSError:
        pass


@pytest.fixture(scope="function")
def db_session():
    """
    Provide a clean database session for each test.
    Rolls back after each test for isolation.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Provide a test client with overridden database dependency.
    Each test gets a fresh, isolated database state.
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for tests."""
    return {
        "identifier": "testuser@example.com",
        "password": "testpass123"
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Create and return a registered user with token."""
    response = client.post("/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()["data"]
    return {
        "user": data["user"],
        "token": data["token"]["access_token"],
        "credentials": test_user_data,
    }





