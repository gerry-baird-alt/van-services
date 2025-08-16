import pytest
from fastapi.testclient import TestClient
from datetime import date
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


class TestVehicleEndpoints:
    def test_get_all_vehicles(self, client):
        """Test getting all vehicles."""
        response = client.get("/vehicle")
        assert response.status_code == 200
        
        vehicles = response.json()
        assert len(vehicles) == 3
        
        # Check first vehicle structure
        vehicle = vehicles[0]
        assert "id" in vehicle
        assert "category" in vehicle
        assert "manufacturer" in vehicle
        assert "model" in vehicle
        assert "daily_rental_rate" in vehicle
        assert "number_of_seats" in vehicle
    
    def test_get_vehicle_by_id(self, client):
        """Test getting a specific vehicle by ID."""
        response = client.get("/vehicle/1")
        assert response.status_code == 200
        
        vehicle = response.json()
        assert vehicle["id"] == 1
        assert vehicle["category"] == "Small"
        assert vehicle["manufacturer"] == "Ford"
        assert vehicle["model"] == "Courier"
    
    def test_get_nonexistent_vehicle(self, client):
        """Test getting a vehicle that doesn't exist."""
        response = client.get("/vehicle/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Vehicle not found"}
    
    def test_create_vehicle(self, client):
        """Test creating a new vehicle."""
        new_vehicle = {
            "category": "Large",
            "manufacturer": "Mercedes",
            "model": "Sprinter",
            "daily_rental_rate": 85.0,
            "number_of_seats": 12
        }
        
        response = client.post("/vehicle", json=new_vehicle)
        assert response.status_code == 200
        
        vehicle = response.json()
        assert vehicle["category"] == "Large"
        assert vehicle["manufacturer"] == "Mercedes"
        assert vehicle["model"] == "Sprinter"
        assert vehicle["daily_rental_rate"] == 85.0
        assert vehicle["number_of_seats"] == 12
        assert "id" in vehicle
        assert vehicle["id"] > 0


class TestBookingEndpoints:
    def test_get_all_bookings(self, client):
        """Test getting all bookings."""
        response = client.get("/booking")
        assert response.status_code == 200
        
        bookings = response.json()
        assert len(bookings) == 3
        
        # Check first booking structure
        booking = bookings[0]
        assert "booking_id" in booking
        assert "vehicle_id" in booking
        assert "start_date" in booking
        assert "end_date" in booking
        assert "customer_name" in booking
        assert "cost" in booking
    
    def test_get_booking_by_id(self, client):
        """Test getting a specific booking by ID."""
        response = client.get("/booking/1")
        assert response.status_code == 200
        
        booking = response.json()
        assert booking["booking_id"] == 1
        assert booking["vehicle_id"] == 1
        assert booking["customer_name"] == "John Smith"
        assert booking["start_date"] == "2024-08-15"
        assert booking["end_date"] == "2024-08-20"
    
    def test_get_nonexistent_booking(self, client):
        """Test getting a booking that doesn't exist."""
        response = client.get("/booking/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Booking not found"}
    
    def test_create_booking_success(self, client):
        """Test creating a new booking successfully."""
        new_booking = {
            "category": "Small",
            "start_date": "2025-01-01",
            "duration": 2,
            "customer_name": "Jane Doe"
        }
        
        response = client.post("/booking", json=new_booking)
        assert response.status_code == 200
        
        booking = response.json()
        assert booking["customer_name"] == "Jane Doe"
        assert booking["start_date"] == "2025-01-01"
        assert booking["end_date"] == "2025-01-02"
        assert "booking_id" in booking
        assert "vehicle_id" in booking
        assert "cost" in booking
        assert booking["cost"] > 0
    
    def test_create_booking_no_availability(self, client):
        """Test creating a booking when no vehicles are available."""
        new_booking = {
            "category": "Small",
            "start_date": "2024-08-15",  # Date that conflicts with existing booking
            "duration": 3,
            "customer_name": "Jane Doe"
        }
        
        response = client.post("/booking", json=new_booking)
        assert response.status_code == 400
        assert "No vehicles" in response.json()["detail"]


class TestScheduleEndpoints:
    def test_get_all_schedule(self, client):
        """Test getting all schedule entries."""
        response = client.get("/schedule")
        assert response.status_code == 200
        
        schedule = response.json()
        assert len(schedule) > 0
        
        # Check first schedule entry structure
        entry = schedule[0]
        assert "date" in entry
        assert "vehicle_id" in entry
        assert "status" in entry
        assert "booking_id" in entry or entry["booking_id"] is None
    
    def test_get_vehicle_schedule(self, client):
        """Test getting schedule for a specific vehicle."""
        response = client.get("/schedule/vehicle/1")
        assert response.status_code == 200
        
        schedule = response.json()
        assert len(schedule) > 0
        
        # All entries should be for vehicle 1
        for entry in schedule:
            assert entry["vehicle_id"] == 1
    
    def test_get_schedule_for_nonexistent_vehicle(self, client):
        """Test getting schedule for a vehicle that doesn't exist."""
        response = client.get("/schedule/vehicle/999")
        assert response.status_code == 200
        
        schedule = response.json()
        assert len(schedule) == 0


class TestScheduleSearchEndpoint:
    def test_search_available_vehicles_success(self, client):
        """Test searching for available vehicles with valid criteria."""
        search_data = {
            "category": "Small",
            "start_date": "2024-08-23",
            "duration": 3
        }
        
        response = client.post("/schedule/search", json=search_data)
        assert response.status_code == 200
        
        results = response.json()
        assert isinstance(results, list)
        
        # Check structure of results if any are returned
        if results:
            result = results[0]
            assert "vehicle_id" in result
            assert "category" in result
            assert "manufacturer" in result
            assert "model" in result
            assert "daily_rental_rate" in result
            assert "number_of_seats" in result
            assert "total_cost" in result
            assert result["category"] == "Small"
    
    def test_search_unavailable_period(self, client):
        """Test searching during a period when vehicles are booked."""
        search_data = {
            "category": "Small",
            "start_date": "2024-08-15",
            "duration": 2
        }
        
        response = client.post("/schedule/search", json=search_data)
        assert response.status_code == 200
        
        results = response.json()
        # Should return empty list or vehicles not conflicting with bookings
        assert isinstance(results, list)
    
    def test_search_nonexistent_category(self, client):
        """Test searching for a category that doesn't exist."""
        search_data = {
            "category": "NonExistent",
            "start_date": "2024-08-25",
            "duration": 1
        }
        
        response = client.post("/schedule/search", json=search_data)
        assert response.status_code == 200
        
        results = response.json()
        assert results == []
    
    def test_search_invalid_data(self, client):
        """Test search with invalid request data."""
        search_data = {
            "category": "Small",
            "start_date": "invalid-date",
            "duration": 3
        }
        
        response = client.post("/schedule/search", json=search_data)
        assert response.status_code == 422  # Validation error
    
    def test_search_missing_fields(self, client):
        """Test search with missing required fields."""
        search_data = {
            "category": "Small"
            # Missing start_date and duration
        }
        
        response = client.post("/schedule/search", json=search_data)
        assert response.status_code == 422  # Validation error
    
    def test_search_total_cost_calculation(self, client):
        """Test that total cost is calculated correctly."""
        search_data = {
            "category": "Medium",
            "start_date": "2024-09-01",
            "duration": 5
        }
        
        response = client.post("/schedule/search", json=search_data)
        assert response.status_code == 200
        
        results = response.json()
        if results:
            result = results[0]
            expected_total = result["daily_rental_rate"] * search_data["duration"]
            assert result["total_cost"] == expected_total