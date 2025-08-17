import pytest
from fastapi.testclient import TestClient
import os
import tempfile
from main import app
from database import init_db, insert_sample_data


@pytest.fixture
def client():
    """Create a test client with a fresh temporary database for each test."""
    # Create a temporary database file for this test
    db_fd, db_path = tempfile.mkstemp()
    
    # Override the database path for testing
    import database.database
    original_db_path = database.database._test_db_path
    database.database._test_db_path = db_path
    
    # Initialize and populate test database
    init_db()
    insert_sample_data()
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore original path and cleanup
    database.database._test_db_path = original_db_path
    os.close(db_fd)
    os.unlink(db_path)