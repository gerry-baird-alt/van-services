import pytest


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


class TestScheduleSearch:
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