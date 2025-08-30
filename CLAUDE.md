# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Install dependencies
uv sync

# Run the FastAPI development server
uv run uvicorn main:app --reload

# Run in Docker
docker build -t van-services .
docker run -p 8000:8000 van-services
```

### Testing
```bash
# Run all tests
pytest tests/

# Run tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_vehicles.py -v

# Run specific test class
pytest tests/test_vehicles.py::TestVehicleEndpoints -v

# Run tests for specific functionality
pytest tests/test_bookings.py -v
pytest tests/test_schedules.py -v
pytest tests/test_admin.py -v
```

### Testing Endpoints Manually
The application serves API endpoints at http://localhost:8000. FastAPI provides automatic API documentation at http://localhost:8000/docs (Swagger UI).

## Architecture Overview

This is a FastAPI-based van rental service with a three-layer architecture:

### Core Components

**Models Layer** (`model/`):
- Pydantic models defining the core data structures
- `Vehicle`: Van rental fleet with pricing and capacity
- `Booking`: Customer reservations with dates and costs
- `Branch`: Physical rental locations with name, address, and city
- `Availability`: Search requests and available vehicle responses
- Each model includes both base and create variants for API operations

**Database Layer** (`database/`):
- SQLite database with foreign key relationships
- `database.py`: Connection management and table creation
- `models.py`: Database access objects (VehicleDB, BookingDB, BranchDB, ScheduleDB)
- Foreign key relationships: 
  - `vehicles.branch_id → branches.branch_id`
  - `bookings.vehicle_id → vehicles.id` and `bookings.branch_id → branches.branch_id`
  - `schedule.vehicle_id → vehicles.id` and `schedule.booking_id → bookings.booking_id`

**API Layer** (`routes/` and `main.py`):
- FastAPI application with modular router structure
- Automatic database initialization with sample data on startup via lifespan events
- Route modules: `vehicles`, `bookings`, `branches`, `availability`, `admin`
- Each route module handles CRUD operations for its respective domain

### Database Schema

The SQLite database (`van_rental.db`) uses these key relationships:
- `branches` table: Contains physical rental locations with branch_id, branch_name, address, and city
- `vehicles` table: References branches through branch_id foreign key
- `bookings` table: References both vehicles and branches through foreign keys
- `schedule` table has composite primary key (date, vehicle_id)
- Foreign keys ensure referential integrity between branches, vehicles, bookings, and schedule entries
- Schedule entries can be "booked" (with booking_id), "available", or "maintenance"

### Data Flow

1. Application startup triggers database initialization and sample data insertion
2. API endpoints use database model classes to query SQLite
3. Pydantic models handle request/response serialization
4. Database models convert between SQLite rows and Pydantic objects

### Key Design Patterns

- **Repository Pattern**: Database access is abstracted through `*DB` classes
- **Dependency Injection**: Database connection management is centralized
- **Foreign Key Constraints**: Ensure data integrity across related entities
- **Composite Keys**: Schedule uses (date, vehicle_id) as primary key for daily tracking