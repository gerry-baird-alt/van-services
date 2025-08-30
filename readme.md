# Van Services API

A FastAPI-based van rental service that provides vehicle booking management across multiple branch locations.

## Overview

This application is a complete van rental management system with the following core functionality:
- **Vehicle Management**: Track rental fleet across multiple branches
- **Branch Management**: Manage rental locations with city information
- **Booking System**: Handle customer reservations with date validation
- **Availability Search**: Find available vehicles by date range, category, and location
- **Administrative Tools**: Database management and reset capabilities

### Architecture

The application follows a three-layer architecture:
- **Models Layer** (`model/`): Pydantic data models for API serialization
- **Database Layer** (`database/`): SQLite database with repository pattern
- **API Layer** (`routes/`, `main.py`): FastAPI routers with modular endpoint organization

### Database Schema

- `branches`: Physical rental locations (branch_id, branch_name, address, city)
- `vehicles`: Rental fleet linked to branches (id, category, manufacturer, model, daily_rate, seats, branch_id)
- `bookings`: Customer reservations (booking_id, vehicle_id, dates, customer_name, cost, branch_id)

## Quick Start

### Installation
```bash
# Install dependencies
uv sync

# Run the development server
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000` with automatic documentation at `http://localhost:8000/docs`.

### Docker
```bash
docker build -t van-services .
docker run -p 8000:8000 van-services
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_vehicles.py -v
pytest tests/test_bookings.py -v
pytest tests/test_admin.py -v
```

## API Endpoints

### Vehicles (`/vehicle`)

**GET /vehicle**
- Returns all vehicles in the fleet
- Response: List of vehicles with pricing and branch information

**GET /vehicle/{vehicle_id}**
- Get specific vehicle by ID
- Response: Vehicle details or 404 if not found

**POST /vehicle**
- Create a new vehicle
- Request body: `VehicleCreate` (category, manufacturer, model, daily_rental_rate, number_of_seats, branch_id)
- Validates branch exists before creation
- Response: Created vehicle with assigned ID

### Bookings (`/booking`)

**GET /booking**
- Returns all bookings in the system
- Response: List of all customer reservations

**GET /booking/{booking_id}**
- Get specific booking by ID  
- Response: Booking details or 404 if not found

**POST /booking**
- Create a new booking
- Request body: `BookingCreate` (category, start_date, end_date, customer_name, branch_id)
- Validates:
  - Branch exists
  - Date range is valid (start ≤ end, not in past)
  - Vehicle availability for requested category/dates/branch
- Automatically selects first available vehicle and calculates total cost
- Response: Created booking with vehicle assignment and pricing

**POST /booking/cancel**
- Cancel an existing booking
- Request body: `BookingCancel` (booking_id, start_date, customer_name)
- Requires exact match of booking ID, start date, and customer name for security
- Response: Success message or 404 if booking not found

### Branches (`/branches`)

**GET /branches/**
- Returns all branch locations
- Response: List of branches with address and city information

**GET /branches/{branch_id}**
- Get specific branch by ID
- Response: Branch details or 404 if not found

**POST /branches/**
- Create a new branch location
- Request body: `BranchCreate` (branch_name, address, city)
- Response: Created branch with assigned ID

### Availability Search (`/availability`)

**POST /availability/search**
- Search for available vehicles
- Request body: `AvailabilityRequest` (start_date, end_date, optional category, optional branch_id)
- Validates:
  - Date range is valid (start ≤ end, not in past)
  - Branch exists (if specified)
- Filtering options:
  - No filters: All available vehicles across all branches
  - Category only: Vehicles of specific category from all branches
  - Branch only: All available vehicles from specific branch
  - Both: Vehicles of specific category from specific branch
- Response: List of `AvailableVehicle` with calculated total cost for date range

### Administration (`/admin`)

**DELETE /admin/data**
- Delete all data from the database
- Use with caution - removes all vehicles, bookings, and branches
- Response: Success confirmation

**POST /admin/reset**
- Reset database to initial state with sample data
- Deletes all existing data and reloads default vehicles, branches, and bookings
- Response: Success confirmation or error details

## Sample Data

The application initializes with sample data:
- **Branches**: Downtown (New York), Airport (Los Angeles), Suburban (Chicago)
- **Vehicles**: Small van (Ford Courier), Medium van (Ford Transit), Large van (Ford Jumbo)
- **Bookings**: Sample reservations for testing

## Error Handling

All endpoints include comprehensive validation:
- 400: Invalid request data, date validation, availability conflicts
- 404: Resource not found (vehicles, bookings, branches)
- 500: Database or system errors

## Development Notes

- Database automatically initializes on startup with sample data
- Foreign key constraints ensure data integrity
- Decimal precision maintained for pricing calculations
- Date validation prevents past bookings and invalid ranges
- Modular router structure for maintainable code organization