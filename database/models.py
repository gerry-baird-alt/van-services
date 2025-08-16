from decimal import Decimal
from datetime import date, timedelta
from typing import List, Optional
from .database import get_db_connection
from model import Vehicle, Booking, Schedule, VehicleSearchResult


class VehicleDB:
    @staticmethod
    def get_all() -> List[Vehicle]:
        """Get all vehicles from database."""
        conn = get_db_connection()
        vehicles = conn.execute('SELECT * FROM vehicles').fetchall()
        conn.close()
        
        return [Vehicle(
            id=row['id'],
            category=row['category'],
            manufacturer=row['manufacturer'],
            model=row['model'],
            daily_rental_rate=Decimal(str(row['daily_rental_rate'])),
            number_of_seats=row['number_of_seats']
        ) for row in vehicles]
    
    @staticmethod
    def get_by_id(vehicle_id: int) -> Optional[Vehicle]:
        """Get a vehicle by ID."""
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,)).fetchone()
        conn.close()
        
        if row:
            return Vehicle(
                id=row['id'],
                category=row['category'],
                manufacturer=row['manufacturer'],
                model=row['model'],
                daily_rental_rate=Decimal(str(row['daily_rental_rate'])),
                number_of_seats=row['number_of_seats']
            )
        return None
    
    @staticmethod
    def create(vehicle: Vehicle) -> Vehicle:
        """Create a new vehicle in database."""
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO vehicles (category, manufacturer, model, daily_rental_rate, number_of_seats)
            VALUES (?, ?, ?, ?, ?)
        ''', (vehicle.category, vehicle.manufacturer, vehicle.model, 
              float(vehicle.daily_rental_rate), vehicle.number_of_seats))
        
        vehicle.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return vehicle


class BookingDB:
    @staticmethod
    def get_all() -> List[Booking]:
        """Get all bookings from database."""
        conn = get_db_connection()
        bookings = conn.execute('SELECT * FROM bookings').fetchall()
        conn.close()
        
        return [Booking(
            booking_id=row['booking_id'],
            vehicle_id=row['vehicle_id'],
            start_date=date.fromisoformat(row['start_date']),
            end_date=date.fromisoformat(row['end_date']),
            customer_name=row['customer_name'],
            cost=Decimal(str(row['cost']))
        ) for row in bookings]
    
    @staticmethod
    def get_by_id(booking_id: int) -> Optional[Booking]:
        """Get a booking by ID."""
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM bookings WHERE booking_id = ?', (booking_id,)).fetchone()
        conn.close()
        
        if row:
            return Booking(
                booking_id=row['booking_id'],
                vehicle_id=row['vehicle_id'],
                start_date=date.fromisoformat(row['start_date']),
                end_date=date.fromisoformat(row['end_date']),
                customer_name=row['customer_name'],
                cost=Decimal(str(row['cost']))
            )
        return None
    
    @staticmethod
    def create(booking: Booking) -> Booking:
        """Create a new booking in database."""
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO bookings (vehicle_id, start_date, end_date, customer_name, cost)
            VALUES (?, ?, ?, ?, ?)
        ''', (booking.vehicle_id, booking.start_date.isoformat(), 
              booking.end_date.isoformat(), booking.customer_name, float(booking.cost)))
        
        booking.booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking


class ScheduleDB:
    @staticmethod
    def get_all() -> List[Schedule]:
        """Get all schedule entries from database."""
        conn = get_db_connection()
        schedules = conn.execute('SELECT * FROM schedule ORDER BY date, vehicle_id').fetchall()
        conn.close()
        
        return [Schedule(
            date=date.fromisoformat(row['date']),
            vehicle_id=row['vehicle_id'],
            status=row['status'],
            booking_id=row['booking_id']
        ) for row in schedules]
    
    @staticmethod
    def get_by_vehicle_and_date(vehicle_id: int, schedule_date: date) -> Optional[Schedule]:
        """Get a schedule entry by vehicle ID and date."""
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM schedule WHERE vehicle_id = ? AND date = ?', 
                          (vehicle_id, schedule_date.isoformat())).fetchone()
        conn.close()
        
        if row:
            return Schedule(
                date=date.fromisoformat(row['date']),
                vehicle_id=row['vehicle_id'],
                status=row['status'],
                booking_id=row['booking_id']
            )
        return None
    
    @staticmethod
    def get_by_vehicle(vehicle_id: int) -> List[Schedule]:
        """Get all schedule entries for a specific vehicle."""
        conn = get_db_connection()
        schedules = conn.execute('SELECT * FROM schedule WHERE vehicle_id = ? ORDER BY date', 
                                (vehicle_id,)).fetchall()
        conn.close()
        
        return [Schedule(
            date=date.fromisoformat(row['date']),
            vehicle_id=row['vehicle_id'],
            status=row['status'],
            booking_id=row['booking_id']
        ) for row in schedules]
    
    @staticmethod
    def create(schedule: Schedule) -> Schedule:
        """Create a new schedule entry in database."""
        conn = get_db_connection()
        conn.execute('''
            INSERT OR REPLACE INTO schedule (date, vehicle_id, status, booking_id)
            VALUES (?, ?, ?, ?)
        ''', (schedule.date.isoformat(), schedule.vehicle_id, schedule.status, schedule.booking_id))
        
        conn.commit()
        conn.close()
        return schedule
    
    @staticmethod
    def search_available_vehicles(category: str, start_date: date, duration: int) -> List[VehicleSearchResult]:
        """Search for available vehicles by category and date range."""
        conn = get_db_connection()
        
        # Generate all dates in the requested period
        search_dates = [(start_date + timedelta(days=i)).isoformat() for i in range(duration)]
        placeholders = ','.join('?' * len(search_dates))
        
        # Find vehicles of the requested category that are available for all requested dates
        query = f'''
        SELECT DISTINCT v.id, v.category, v.manufacturer, v.model, v.daily_rental_rate, v.number_of_seats
        FROM vehicles v
        WHERE v.category = ?
        AND v.id NOT IN (
            SELECT DISTINCT s.vehicle_id
            FROM schedule s
            WHERE s.date IN ({placeholders})
        )
        '''
        
        params = [category] + search_dates
        vehicles = conn.execute(query, params).fetchall()
        conn.close()
        
        # Convert to search results with total cost calculation
        results = []
        for vehicle in vehicles:
            daily_rate = float(vehicle['daily_rental_rate'])
            total_cost = daily_rate * duration
            
            results.append(VehicleSearchResult(
                vehicle_id=vehicle['id'],
                category=vehicle['category'],
                manufacturer=vehicle['manufacturer'],
                model=vehicle['model'],
                daily_rental_rate=daily_rate,
                number_of_seats=vehicle['number_of_seats'],
                total_cost=total_cost
            ))
        
        return results