import pytest
from datetime import date, timedelta


class TestBookingEndpoints:
    def test_get_all_bookings(self, client):
        """Test getting all bookings."""
        response = client.get("/booking")
        assert response.status_code == 200
        
        bookings = response.json()
        assert len(bookings) >= 3  # At least the sample bookings
        
        # Check first booking structure
        booking = bookings[0]
        assert "booking_id" in booking
        assert "vehicle_id" in booking
        assert "start_date" in booking
        assert "end_date" in booking
        assert "customer_name" in booking
        assert "cost" in booking
        assert "branch_id" in booking
    
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
        future_date = date.today() + timedelta(days=30)
        end_date = future_date + timedelta(days=1)
        
        new_booking = {
            "category": "Small",
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat(),
            "customer_name": "Jane Doe",
            "branch_id": 1
        }
        
        response = client.post("/booking", json=new_booking)
        assert response.status_code == 200
        
        booking = response.json()
        assert booking["customer_name"] == "Jane Doe"
        assert booking["start_date"] == future_date.isoformat()
        assert booking["end_date"] == end_date.isoformat()
        assert "booking_id" in booking
        assert "vehicle_id" in booking
        assert "cost" in booking
        assert "branch_id" in booking
        assert booking["branch_id"] == 1
        assert booking["cost"] > 0
    
    def test_create_booking_no_availability(self, client):
        """Test creating a booking when no vehicles are available."""
        # First create a booking to consume availability
        future_date = date.today() + timedelta(days=45)
        end_date = future_date + timedelta(days=2)
        
        first_booking = {
            "category": "Small",
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat(),
            "customer_name": "First Customer",
            "branch_id": 1
        }
        
        first_response = client.post("/booking", json=first_booking)
        assert first_response.status_code == 200
        
        # Now try to book the same category/branch for overlapping dates
        # This should fail due to no availability (assuming only 1 Small vehicle at branch 1)
        conflicting_booking = {
            "category": "Small", 
            "start_date": (future_date + timedelta(days=1)).isoformat(),
            "end_date": (future_date + timedelta(days=3)).isoformat(),
            "customer_name": "Jane Doe",
            "branch_id": 1
        }
        
        response = client.post("/booking", json=conflicting_booking)
        assert response.status_code == 400
        assert "No vehicles" in response.json()["detail"]
    
    def test_create_booking_invalid_branch(self, client):
        """Test creating a booking with invalid branch_id."""
        future_date = date.today() + timedelta(days=15)
        end_date = future_date + timedelta(days=1)
        
        new_booking = {
            "category": "Small",
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat(),
            "customer_name": "Jane Doe",
            "branch_id": 999  # Non-existent branch
        }
        
        response = client.post("/booking", json=new_booking)
        assert response.status_code == 400
        assert "Branch with ID 999 does not exist" in response.json()["detail"]
    
    def test_create_booking_invalid_date_range(self, client):
        """Test creating a booking with invalid date range (start after end)."""
        future_date = date.today() + timedelta(days=10)
        past_date = future_date - timedelta(days=5)
        
        new_booking = {
            "category": "Small",
            "start_date": future_date.isoformat(),
            "end_date": past_date.isoformat(),  # End before start
            "customer_name": "Jane Doe",
            "branch_id": 1
        }
        
        response = client.post("/booking", json=new_booking)
        assert response.status_code == 400
        assert "Start date must be before or equal to end date" in response.json()["detail"]
    
    def test_create_booking_past_date(self, client):
        """Test creating a booking with past start date."""
        new_booking = {
            "category": "Small",
            "start_date": "2020-01-01",  # Past date
            "end_date": "2020-01-02",
            "customer_name": "Jane Doe",
            "branch_id": 1
        }
        
        response = client.post("/booking", json=new_booking)
        assert response.status_code == 400
        assert "Start date cannot be in the past" in response.json()["detail"]


class TestBookingCancellation:
    def test_create_and_cancel_booking(self, client):
        """Test creating a booking, then cancelling it, and confirming deletion."""
        # Step 1: Create a new booking
        future_date = date.today() + timedelta(days=60)
        end_date = future_date + timedelta(days=1)
        
        new_booking = {
            "category": "Small",
            "start_date": future_date.isoformat(),
            "end_date": end_date.isoformat(),
            "customer_name": "Test Customer",
            "branch_id": 1
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
    
    def test_cancel_existing_booking(self, client):
        """Test cancelling an existing booking."""
        # Use an existing booking from sample data
        cancel_data = {
            "booking_id": 1,
            "start_date": "2024-08-15", 
            "customer_name": "John Smith"
        }
        
        # First verify the booking exists
        booking_response = client.get("/booking/1")
        assert booking_response.status_code == 200
        
        # Cancel the booking
        cancel_response = client.post("/booking/cancel", json=cancel_data)
        assert cancel_response.status_code == 200
        assert cancel_response.json() == {"message": "Booking cancelled successfully"}
        
        # Verify booking is deleted
        deleted_booking_response = client.get("/booking/1")
        assert deleted_booking_response.status_code == 404