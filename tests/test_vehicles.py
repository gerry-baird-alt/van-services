import pytest


class TestVehicleEndpoints:
    def test_get_all_vehicles(self, client):
        """Test getting all vehicles."""
        response = client.get("/vehicle")
        assert response.status_code == 200
        
        vehicles = response.json()
        assert len(vehicles) >= 3  # At least the sample vehicles
        
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