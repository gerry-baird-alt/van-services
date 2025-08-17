import pytest


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


class TestBookingCancellation:
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