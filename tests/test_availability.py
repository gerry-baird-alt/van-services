import pytest
from datetime import date, timedelta


class TestAvailabilityEndpoints:
    def test_search_available_vehicles_all_filters(self, client):
        """Test searching for available vehicles with all filters."""
        # Search for Small category vehicles at branch 1 for future dates
        future_date = date.today() + timedelta(days=30)
        end_date = future_date + timedelta(days=2)
        
        search_request = {
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat(),
            "category": "Small",
            "branch_id": 1
        }
        
        response = client.post("/availability/search", json=search_request)
        assert response.status_code == 200
        
        vehicles = response.json()
        assert isinstance(vehicles, list)
        
        # If there are results, verify they match our criteria
        for vehicle in vehicles:
            assert "vehicle_id" in vehicle
            assert vehicle["category"] == "Small"
            assert vehicle["branch_id"] == 1
            assert "manufacturer" in vehicle
            assert "model" in vehicle
            assert "daily_rental_rate" in vehicle
            assert "number_of_seats" in vehicle
            assert "total_cost" in vehicle
            # Total cost should be daily rate * 3 days
            expected_cost = vehicle["daily_rental_rate"] * 3
            assert vehicle["total_cost"] == expected_cost
    
    def test_search_available_vehicles_category_only(self, client):
        """Test searching for available vehicles with category filter only."""
        future_date = date.today() + timedelta(days=60)
        end_date = future_date + timedelta(days=1)
        
        search_request = {
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat(),
            "category": "Medium"
        }
        
        response = client.post("/availability/search", json=search_request)
        assert response.status_code == 200
        
        vehicles = response.json()
        assert isinstance(vehicles, list)
        
        # Verify all results are Medium category
        for vehicle in vehicles:
            assert vehicle["category"] == "Medium"
            # Total cost should be daily rate * 2 days
            expected_cost = vehicle["daily_rental_rate"] * 2
            assert vehicle["total_cost"] == expected_cost
    
    def test_search_available_vehicles_branch_only(self, client):
        """Test searching for available vehicles with branch filter only."""
        future_date = date.today() + timedelta(days=45)
        end_date = future_date
        
        search_request = {
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat(),
            "branch_id": 2
        }
        
        response = client.post("/availability/search", json=search_request)
        assert response.status_code == 200
        
        vehicles = response.json()
        assert isinstance(vehicles, list)
        
        # Verify all results are from branch 2
        for vehicle in vehicles:
            assert vehicle["branch_id"] == 2
            # Total cost should be daily rate * 1 day
            expected_cost = vehicle["daily_rental_rate"] * 1
            assert vehicle["total_cost"] == expected_cost
    
    def test_search_available_vehicles_no_filters(self, client):
        """Test searching for available vehicles with no filters."""
        future_date = date.today() + timedelta(days=90)
        end_date = future_date + timedelta(days=4)
        
        search_request = {
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        response = client.post("/availability/search", json=search_request)
        assert response.status_code == 200
        
        vehicles = response.json()
        assert isinstance(vehicles, list)
        
        # Should return vehicles from all categories and branches
        for vehicle in vehicles:
            assert vehicle["category"] in ["Small", "Medium", "Large"]
            assert vehicle["branch_id"] in [1, 2, 3]
            # Total cost should be daily rate * 5 days
            expected_cost = vehicle["daily_rental_rate"] * 5
            assert vehicle["total_cost"] == expected_cost
    
    def test_search_invalid_date_range(self, client):
        """Test searching with invalid date range (start after end)."""
        future_date = date.today() + timedelta(days=30)
        past_date = future_date - timedelta(days=5)
        
        search_request = {
            "start_date": future_date.isoformat(),
            "end_date": past_date.isoformat()
        }
        
        response = client.post("/availability/search", json=search_request)
        assert response.status_code == 400
        assert "Start date must be before or equal to end date" in response.json()["detail"]
    
    def test_search_past_date(self, client):
        """Test searching with past start date."""
        past_date = date.today() - timedelta(days=1)
        end_date = past_date + timedelta(days=2)
        
        search_request = {
            "start_date": past_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        response = client.post("/availability/search", json=search_request)
        assert response.status_code == 400
        assert "Start date cannot be in the past" in response.json()["detail"]
    
    def test_search_invalid_branch(self, client):
        """Test searching with non-existent branch."""
        future_date = date.today() + timedelta(days=30)
        end_date = future_date + timedelta(days=1)
        
        search_request = {
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat(),
            "branch_id": 999
        }
        
        response = client.post("/availability/search", json=search_request)
        assert response.status_code == 400
        assert "Branch with ID 999 does not exist" in response.json()["detail"]
    
    def test_search_same_start_end_date(self, client):
        """Test searching with same start and end date."""
        future_date = date.today() + timedelta(days=15)
        
        search_request = {
            "start_date": future_date.isoformat(),
            "end_date": future_date.isoformat(),
            "category": "Large"
        }
        
        response = client.post("/availability/search", json=search_request)
        assert response.status_code == 200
        
        vehicles = response.json()
        # Verify all results have correct total cost for 1 day
        for vehicle in vehicles:
            assert vehicle["category"] == "Large"
            expected_cost = vehicle["daily_rental_rate"] * 1
            assert vehicle["total_cost"] == expected_cost
    
    def test_search_conflicting_with_existing_booking(self, client):
        """Test that vehicles with existing bookings are not returned."""
        # First create a booking for a specific future period
        future_date = date.today() + timedelta(days=7)
        
        booking_request = {
            "category": "Small",
            "start_date": future_date.isoformat(),
            "end_date": (future_date + timedelta(days=1)).isoformat(),
            "customer_name": "Test Customer",
            "branch_id": 1
        }
        
        booking_response = client.post("/booking", json=booking_request)
        assert booking_response.status_code == 200
        
        booked_vehicle_id = booking_response.json()["vehicle_id"]
        
        # Now search for availability during the same period
        search_request = {
            "start_date": future_date.isoformat(),
            "end_date": (future_date + timedelta(days=1)).isoformat(),
            "category": "Small",
            "branch_id": 1
        }
        
        availability_response = client.post("/availability/search", json=search_request)
        assert availability_response.status_code == 200
        
        available_vehicles = availability_response.json()
        
        # The booked vehicle should not be in the available list
        available_vehicle_ids = [v["vehicle_id"] for v in available_vehicles]
        assert booked_vehicle_id not in available_vehicle_ids