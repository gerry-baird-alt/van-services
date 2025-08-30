from decimal import Decimal
from datetime import date, timedelta
from typing import List, Optional
from .database import get_db_connection
from model import Vehicle, Booking, Branch


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
            number_of_seats=row['number_of_seats'],
            branch_id=row['branch_id']
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
                number_of_seats=row['number_of_seats'],
                branch_id=row['branch_id']
            )
        return None
    
    @staticmethod
    def create(vehicle: Vehicle) -> Vehicle:
        """Create a new vehicle in database."""
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO vehicles (category, manufacturer, model, daily_rental_rate, number_of_seats, branch_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (vehicle.category, vehicle.manufacturer, vehicle.model, 
              float(vehicle.daily_rental_rate), vehicle.number_of_seats, vehicle.branch_id))
        
        vehicle.id = cursor.lastrowid
        conn.commit()
        conn.close()
        return vehicle
    
    @staticmethod
    def get_available_vehicles(category: str, start_date: date, end_date: date, branch_id: int) -> List[Vehicle]:
        """Get vehicles available for booking in the specified date range and branch."""
        conn = get_db_connection()
        
        # Find vehicles that don't have conflicting bookings
        query = '''
        SELECT DISTINCT v.*
        FROM vehicles v
        WHERE v.category = ? AND v.branch_id = ?
        AND v.id NOT IN (
            SELECT DISTINCT b.vehicle_id
            FROM bookings b
            WHERE (b.start_date <= ? AND b.end_date >= ?)
               OR (b.start_date <= ? AND b.end_date >= ?)
               OR (b.start_date >= ? AND b.end_date <= ?)
        )
        '''
        
        vehicles = conn.execute(query, (
            category, branch_id,
            end_date.isoformat(), start_date.isoformat(),
            start_date.isoformat(), start_date.isoformat(),
            start_date.isoformat(), end_date.isoformat()
        )).fetchall()
        conn.close()
        
        return [Vehicle(
            id=row['id'],
            category=row['category'],
            manufacturer=row['manufacturer'],
            model=row['model'],
            daily_rental_rate=Decimal(str(row['daily_rental_rate'])),
            number_of_seats=row['number_of_seats'],
            branch_id=row['branch_id']
        ) for row in vehicles]


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
            cost=Decimal(str(row['cost'])),
            branch_id=row['branch_id']
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
                cost=Decimal(str(row['cost'])),
                branch_id=row['branch_id']
            )
        return None
    
    
    @staticmethod
    def create(booking: Booking) -> Booking:
        """Create a new booking in database."""
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO bookings (vehicle_id, start_date, end_date, customer_name, cost, branch_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (booking.vehicle_id, booking.start_date.isoformat(), 
              booking.end_date.isoformat(), booking.customer_name, float(booking.cost), booking.branch_id))
        
        booking.booking_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return booking
    
    @staticmethod
    def delete(booking_id: int, start_date: date, customer_name: str) -> bool:
        """Delete a booking by ID, start date, and customer name."""
        conn = get_db_connection()
        
        # First verify the booking exists with matching criteria
        booking = conn.execute(
            'SELECT * FROM bookings WHERE booking_id = ? AND start_date = ? AND customer_name = ?', 
            (booking_id, start_date.isoformat(), customer_name)
        ).fetchone()
        
        if not booking:
            conn.close()
            return False
        
        # Delete the booking
        cursor = conn.execute(
            'DELETE FROM bookings WHERE booking_id = ? AND start_date = ? AND customer_name = ?', 
            (booking_id, start_date.isoformat(), customer_name)
        )
        
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    




class BranchDB:
    @staticmethod
    def get_all() -> List[Branch]:
        """Get all branches from database."""
        conn = get_db_connection()
        branches = conn.execute('SELECT * FROM branches').fetchall()
        conn.close()
        
        return [Branch(
            branch_id=row['branch_id'],
            branch_name=row['branch_name'],
            address=row['address'],
            city=row['city']
        ) for row in branches]
    
    @staticmethod
    def get_by_id(branch_id: int) -> Optional[Branch]:
        """Get a branch by ID."""
        conn = get_db_connection()
        row = conn.execute('SELECT * FROM branches WHERE branch_id = ?', (branch_id,)).fetchone()
        conn.close()
        
        if row:
            return Branch(
                branch_id=row['branch_id'],
                branch_name=row['branch_name'],
                address=row['address'],
                city=row['city']
            )
        return None
    
    @staticmethod
    def create(branch: Branch) -> Branch:
        """Create a new branch in database."""
        conn = get_db_connection()
        cursor = conn.execute('''
            INSERT INTO branches (branch_name, address, city)
            VALUES (?, ?, ?)
        ''', (branch.branch_name, branch.address, branch.city))
        
        branch.branch_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return branch
