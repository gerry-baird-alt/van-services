import sqlite3
import os
from decimal import Decimal
from datetime import date


def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect('van_rental.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with tables."""
    conn = get_db_connection()
    
    # Create vehicles table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            model TEXT NOT NULL,
            daily_rental_rate REAL NOT NULL,
            number_of_seats INTEGER NOT NULL
        )
    ''')
    
    # Create bookings table with foreign key to vehicles
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            customer_name TEXT NOT NULL,
            cost REAL NOT NULL,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')
    
    # Create schedule table with foreign keys to vehicles and bookings
    conn.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            date DATE NOT NULL,
            vehicle_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            booking_id INTEGER,
            PRIMARY KEY (date, vehicle_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
            FOREIGN KEY (booking_id) REFERENCES bookings (booking_id)
        )
    ''')
    
    conn.commit()
    conn.close()


def insert_sample_data():
    """Insert sample data into the database."""
    conn = get_db_connection()
    
    # Clear existing data
    conn.execute('DELETE FROM schedule')
    conn.execute('DELETE FROM bookings')
    conn.execute('DELETE FROM vehicles')
    
    # Insert sample vehicles
    vehicles = [
        (1, 'Small', 'Ford', 'Courier', 55.00, 8),
        (2, 'Medium', 'Ford', 'Transit', 85.00, 2),
        (3, 'Large', 'Ford', 'Jumbo', 95.00, 12)
    ]
    
    conn.executemany('''
        INSERT INTO vehicles (id, category, manufacturer, model, daily_rental_rate, number_of_seats)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', vehicles)
    
    # Insert sample bookings
    bookings = [
        (1, 1, '2024-08-15', '2024-08-20', 'John Smith', 375.00),
        (2, 2, '2024-08-18', '2024-08-22', 'Jane Doe', 220.00),
        (3, 3, '2024-08-25', '2024-08-30', 'Bob Johnson', 475.00)
    ]
    
    conn.executemany('''
        INSERT INTO bookings (booking_id, vehicle_id, start_date, end_date, customer_name, cost)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', bookings)
    
    # Insert sample schedule data
    schedules = [
        ('2024-08-15', 1, 'booked', 1),
        ('2024-08-16', 1, 'booked', 1),
        ('2024-08-17', 1, 'booked', 1),
        ('2024-08-18', 1, 'booked', 1),
        ('2024-08-19', 1, 'booked', 1),
        ('2024-08-20', 1, 'booked', 1),
        ('2024-08-18', 2, 'booked', 2),
        ('2024-08-19', 2, 'booked', 2),
        ('2024-08-20', 2, 'booked', 2),
        ('2024-08-21', 2, 'booked', 2),
        ('2024-08-22', 2, 'booked', 2),
        ('2024-08-25', 3, 'booked', 3),
        ('2024-08-26', 3, 'booked', 3),
        ('2024-08-27', 3, 'booked', 3),
        ('2024-08-28', 3, 'booked', 3),
        ('2024-08-29', 3, 'booked', 3),
        ('2024-08-30', 3, 'booked', 3),
        ('2024-08-31', 3, 'maintenance', None)
    ]
    
    conn.executemany('''
        INSERT INTO schedule (date, vehicle_id, status, booking_id)
        VALUES (?, ?, ?, ?)
    ''', schedules)
    
    conn.commit()
    conn.close()