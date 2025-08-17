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
    
    def test_create_and_cancel_booking(self, client):
        """Test creating a booking, then cancelling it, and confirming deletion."""
        # Step 1: Create a new booking
        new_booking = {
            "category": "Small",
            "start_date": "2025-03-01",
            "duration": 2,
            "customer_name": "Test Customer"
        }
        
        create_response = client.post("/booking", json=new_booking)
        assert create_response.status_code == 200
        
        created_booking = create_response.json()
        booking_id = created_booking["booking_id"]
        start_date = created_booking["start_date"]
        customer_name = created_booking["customer_name"]
        
        # Verify booking was created
        get_response = client.get(f"/booking/{booking_id}")
        assert get_response.status_code == 200
        
        # Step 2: Cancel the booking
        cancel_data = {
            "booking_id": booking_id,
            "start_date": start_date,
            "customer_name": customer_name
        }
        
        cancel_response = client.post("/booking/cancel", json=cancel_data)
        assert cancel_response.status_code == 200
        assert cancel_response.json() == {"message": "Booking cancelled successfully"}
        
        # Step 3: Confirm booking has been deleted
        get_deleted_response = client.get(f"/booking/{booking_id}")
        assert get_deleted_response.status_code == 404
        assert get_deleted_response.json() == {"detail": "Booking not found"}
        
        # Step 4: Verify schedule entries have been removed
        schedule_response = client.get("/schedule")
        assert schedule_response.status_code == 200
        
        schedule_entries = schedule_response.json()
        
        # Check that the previously booked dates no longer exist in schedule
        booking_schedule_entries = [
            entry for entry in schedule_entries
            if (entry["date"] >= start_date and 
                entry["date"] <= created_booking["end_date"] and 
                entry["vehicle_id"] == created_booking["vehicle_id"])
        ]
        assert len(booking_schedule_entries) == 0
    
    def test_cancel_booking_invalid_credentials(self, client):
        """Test cancelling a booking with invalid credentials."""
        # Try to cancel with wrong customer name
        cancel_data = {
            "booking_id": 1,
            "start_date": "2024-08-15",
            "customer_name": "Wrong Customer"
        }
        cancel_response = client.post("/booking/cancel", json=cancel_data)
        assert cancel_response.status_code == 404
        assert cancel_response.json() == {"detail": "Booking not found or invalid credentials"}
        
        # Try to cancel with wrong start date
        cancel_data = {
            "booking_id": 1,
            "start_date": "2024-08-01",
            "customer_name": "John Smith"
        }
        cancel_response = client.post("/booking/cancel", json=cancel_data)
        assert cancel_response.status_code == 404
        assert cancel_response.json() == {"detail": "Booking not found or invalid credentials"}
    
    def test_cancel_nonexistent_booking(self, client):
        """Test cancelling a booking that doesn't exist."""
        cancel_data = {
            "booking_id": 999,
            "start_date": "2024-08-15",
            "customer_name": "John Smith"
        }
        cancel_response = client.post("/booking/cancel", json=cancel_data)
        assert cancel_response.status_code == 404
        assert cancel_response.json() == {"detail": "Booking not found or invalid credentials"}
    
    def test_cancel_existing_booking_removes_schedule(self, client):
        """Test cancelling an existing booking removes schedule entries."""
        # Use an existing booking from sample data
        cancel_data = {
            "booking_id": 1,
            "start_date": "2024-08-15", 
            "customer_name": "John Smith"
        }
        
        # First verify the booking and schedule entries exist
        booking_response = client.get("/booking/1")
        assert booking_response.status_code == 200
        
        schedule_response = client.get("/schedule")
        assert schedule_response.status_code == 200
        initial_schedule = schedule_response.json()
        
        # Find schedule entries for booking 1
        booking_1_entries = [entry for entry in initial_schedule if entry["booking_id"] == 1]
        assert len(booking_1_entries) > 0  # Should have some entries
        
        # Cancel the booking
        cancel_response = client.post("/booking/cancel", json=cancel_data)
        assert cancel_response.status_code == 200
        assert cancel_response.json() == {"message": "Booking cancelled successfully"}
        
        # Verify booking is deleted
        deleted_booking_response = client.get("/booking/1")
        assert deleted_booking_response.status_code == 404
        
        # Verify schedule entries are removed
        final_schedule_response = client.get("/schedule")
        assert final_schedule_response.status_code == 200
        final_schedule = final_schedule_response.json()
        
        # Check that no schedule entries exist for booking 1
        remaining_booking_1_entries = [entry for entry in final_schedule if entry["booking_id"] == 1]
        assert len(remaining_booking_1_entries) == 0


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