import pytest
from fastapi.testclient import TestClient
import os
import tempfile
from main import app
from database import init_db, insert_sample_data


@pytest.fixture
def client():
    """Create a test client with a temporary database."""
    # Create a temporary database file for testing
    db_fd, db_path = tempfile.mkstemp()
    
    # Override the database path for testing
    original_db = "van_rental.db"
    test_db = db_path
    
    # Replace database connection to use test database
    import database.database
    database.database.get_db_connection = lambda: database.database.sqlite3.connect(test_db)
    
    # Initialize test database
    init_db()
    insert_sample_data()
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)