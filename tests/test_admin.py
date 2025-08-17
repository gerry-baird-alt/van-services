import pytest


class TestAdminEndpoints:
    def test_delete_all_data_success(self, client):
        """Test successfully deleting all data from the database."""
        # First create some test data to ensure we have data to delete
        new_vehicle = {
            "category": "Test",
            "manufacturer": "Test Motors",
            "model": "Test Van",
            "daily_rental_rate": 50.0,
            "number_of_seats": 4
        }
        vehicle_response = client.post("/vehicle", json=new_vehicle)
        assert vehicle_response.status_code == 200
        
        # Get initial counts
        vehicles_response = client.get("/vehicle")
        assert vehicles_response.status_code == 200
        initial_vehicle_count = len(vehicles_response.json())
        assert initial_vehicle_count > 0  # Should have at least our test vehicle
        
        bookings_response = client.get("/booking")
        assert bookings_response.status_code == 200
        initial_booking_count = len(bookings_response.json())
        
        schedule_response = client.get("/schedule")
        assert schedule_response.status_code == 200
        initial_schedule_count = len(schedule_response.json())
        
        # Delete all data
        delete_response = client.delete("/admin/data")
        assert delete_response.status_code == 200
        assert delete_response.json() == {"message": "All data deleted successfully"}
        
        # Verify all data is gone
        vehicles_after = client.get("/vehicle")
        assert vehicles_after.status_code == 200
        assert len(vehicles_after.json()) == 0
        
        bookings_after = client.get("/booking")
        assert bookings_after.status_code == 200
        assert len(bookings_after.json()) == 0
        
        schedule_after = client.get("/schedule")
        assert schedule_after.status_code == 200
        assert len(schedule_after.json()) == 0
    
    def test_delete_all_data_when_empty(self, client):
        """Test deleting data when database is already empty."""
        # First delete all data
        delete_response_1 = client.delete("/admin/data")
        assert delete_response_1.status_code == 200
        
        # Try to delete again when empty
        delete_response_2 = client.delete("/admin/data")
        assert delete_response_2.status_code == 200
        assert delete_response_2.json() == {"message": "All data deleted successfully"}
    
    def test_operations_after_delete_all_data(self, client):
        """Test that normal operations work after deleting all data."""
        # Delete all data
        delete_response = client.delete("/admin/data")
        assert delete_response.status_code == 200
        
        # Try to get a specific vehicle (should return 404)
        vehicle_response = client.get("/vehicle/1")
        assert vehicle_response.status_code == 404
        
        # Try to get a specific booking (should return 404)
        booking_response = client.get("/booking/1")
        assert booking_response.status_code == 404
        
        # Create a new vehicle after deletion
        new_vehicle = {
            "category": "Test",
            "manufacturer": "Test Motors",
            "model": "Test Van",
            "daily_rental_rate": 50.0,
            "number_of_seats": 4
        }
        
        create_response = client.post("/vehicle", json=new_vehicle)
        assert create_response.status_code == 200
        
        created_vehicle = create_response.json()
        assert created_vehicle["category"] == "Test"
        assert created_vehicle["manufacturer"] == "Test Motors"
        
        # Verify the vehicle was created
        vehicles_response = client.get("/vehicle")
        assert vehicles_response.status_code == 200
        vehicles = vehicles_response.json()
        assert len(vehicles) == 1
        assert vehicles[0]["category"] == "Test"

    def test_reset_database_success(self, client):
        """Test successfully resetting the database with sample data."""
        # First delete all data to ensure we start from empty state
        delete_response = client.delete("/admin/data")
        assert delete_response.status_code == 200
        
        # Verify database is empty
        vehicles_response = client.get("/vehicle")
        assert vehicles_response.status_code == 200
        assert len(vehicles_response.json()) == 0
        
        bookings_response = client.get("/booking")
        assert bookings_response.status_code == 200
        assert len(bookings_response.json()) == 0
        
        schedule_response = client.get("/schedule")
        assert schedule_response.status_code == 200
        assert len(schedule_response.json()) == 0
        
        # Reset database with sample data
        reset_response = client.post("/admin/reset")
        assert reset_response.status_code == 200
        assert reset_response.json() == {"message": "Database reset successfully with sample data"}
        
        # Verify sample data was loaded
        vehicles_after = client.get("/vehicle")
        assert vehicles_after.status_code == 200
        vehicles = vehicles_after.json()
        assert len(vehicles) == 3  # Should have 3 sample vehicles
        
        # Check specific sample vehicles exist
        vehicle_1 = client.get("/vehicle/1")
        assert vehicle_1.status_code == 200
        vehicle_1_data = vehicle_1.json()
        assert vehicle_1_data["category"] == "Small"
        assert vehicle_1_data["manufacturer"] == "Ford"
        assert vehicle_1_data["model"] == "Courier"
        
        vehicle_2 = client.get("/vehicle/2")
        assert vehicle_2.status_code == 200
        vehicle_2_data = vehicle_2.json()
        assert vehicle_2_data["category"] == "Medium"
        assert vehicle_2_data["manufacturer"] == "Ford"
        assert vehicle_2_data["model"] == "Transit"
        
        vehicle_3 = client.get("/vehicle/3")
        assert vehicle_3.status_code == 200
        vehicle_3_data = vehicle_3.json()
        assert vehicle_3_data["category"] == "Large"
        assert vehicle_3_data["manufacturer"] == "Ford"
        assert vehicle_3_data["model"] == "Jumbo"
        
        # Verify sample bookings were loaded
        bookings_after = client.get("/booking")
        assert bookings_after.status_code == 200
        bookings = bookings_after.json()
        assert len(bookings) == 3  # Should have 3 sample bookings
        
        # Check specific sample booking exists
        booking_1 = client.get("/booking/1")
        assert booking_1.status_code == 200
        booking_1_data = booking_1.json()
        assert booking_1_data["customer_name"] == "John Smith"
        assert booking_1_data["vehicle_id"] == 1
        
        # Verify sample schedule was loaded
        schedule_after = client.get("/schedule")
        assert schedule_after.status_code == 200
        schedule = schedule_after.json()
        assert len(schedule) > 0  # Should have schedule entries
        
    def test_reset_database_from_existing_data(self, client):
        """Test resetting database when it already contains data."""
        # Create additional test data first
        new_vehicle = {
            "category": "Test",
            "manufacturer": "Test Motors",
            "model": "Test Van",
            "daily_rental_rate": 50.0,
            "number_of_seats": 4
        }
        vehicle_response = client.post("/vehicle", json=new_vehicle)
        assert vehicle_response.status_code == 200
        
        # Should now have 4 vehicles (3 sample + 1 test)
        vehicles_before = client.get("/vehicle")
        assert vehicles_before.status_code == 200
        assert len(vehicles_before.json()) == 4
        
        # Reset database
        reset_response = client.post("/admin/reset")
        assert reset_response.status_code == 200
        assert reset_response.json() == {"message": "Database reset successfully with sample data"}
        
        # Should now have exactly 3 sample vehicles again
        vehicles_after = client.get("/vehicle")
        assert vehicles_after.status_code == 200
        vehicles = vehicles_after.json()
        assert len(vehicles) == 3
        
        # Verify the test vehicle is gone and only sample vehicles remain
        for vehicle in vehicles:
            assert vehicle["manufacturer"] == "Ford"  # All sample vehicles are Ford
            assert vehicle["category"] in ["Small", "Medium", "Large"]