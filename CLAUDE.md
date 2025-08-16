# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Install dependencies
uv sync

# Run the FastAPI development server
uvicorn main:app --reload

# Run in Docker
docker build -t van-services .
docker run -p 8000:8000 van-services
```

### Testing
```bash
# Run all tests
pytest test_main.py

# Run tests with verbose output
pytest test_main.py -v

# Run specific test class
pytest test_main.py::TestVehicleEndpoints -v
```

### Testing Endpoints Manually
Use the provided `test_main.http` file with VS Code REST Client extension to test API endpoints.

## Architecture Overview

This is a FastAPI-based van rental service with a three-layer architecture:

### Core Components

**Models Layer** (`model/`):
- Pydantic models defining the core data structures
- `Vehicle`: Van rental fleet with pricing and capacity
- `Booking`: Customer reservations with dates and costs  
- `Schedule`: Daily vehicle availability and status tracking

**Database Layer** (`database/`):
- SQLite database with foreign key relationships
- `database.py`: Connection management and table creation
- `models.py`: Database access objects (VehicleDB, BookingDB, ScheduleDB)
- Foreign key relationships: `bookings.vehicle_id → vehicles.id` and `schedule.vehicle_id → vehicles.id`, `schedule.booking_id → bookings.booking_id`

**API Layer** (`main.py`):
- FastAPI application with RESTful endpoints
- Automatic database initialization with sample data on startup
- Endpoints for vehicles, bookings, and schedules

### Database Schema

The SQLite database (`van_rental.db`) uses these key relationships:
- `schedule` table has composite primary key (date, vehicle_id)
- Foreign keys ensure referential integrity between vehicles, bookings, and schedule entries
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