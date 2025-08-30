import sqlite3
import os
from decimal import Decimal
from datetime import date


# Global variable to override database path for testing
_test_db_path = None

def get_db_connection():
    """Get a connection to the SQLite database."""
    db_path = _test_db_path if _test_db_path else 'van_rental.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database with tables."""
    conn = get_db_connection()
    
    # Create branches table first (referenced by vehicles)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_name TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')
    
    # Create vehicles table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            model TEXT NOT NULL,
            daily_rental_rate REAL NOT NULL,
            number_of_seats INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            FOREIGN KEY (branch_id) REFERENCES branches (branch_id)
        )
    ''')
    
    # Create bookings table with foreign key to vehicles and branches
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            customer_name TEXT NOT NULL,
            cost REAL NOT NULL,
            branch_id INTEGER NOT NULL,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
            FOREIGN KEY (branch_id) REFERENCES branches (branch_id)
        )
    ''')
    
    
    conn.commit()
    conn.close()


def delete_data():
    """Completely reset database by dropping and recreating tables."""
    conn = get_db_connection()
    
    # Enable foreign keys to ensure proper cascade
    conn.execute('PRAGMA foreign_keys = ON')
    
    # Drop all tables in correct order (respecting foreign keys)
    conn.execute('DROP TABLE IF EXISTS bookings')
    conn.execute('DROP TABLE IF EXISTS vehicles')
    conn.execute('DROP TABLE IF EXISTS branches')
    
    # Clear any remaining sqlite_sequence entries (if table exists)
    try:
        conn.execute('DELETE FROM sqlite_sequence WHERE name IN ("vehicles", "bookings", "branches")')
    except sqlite3.OperationalError:
        # sqlite_sequence table doesn't exist yet, which is fine
        pass
    
    # Recreate tables
    conn.execute('''
        CREATE TABLE branches (
            branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_name TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')
    
    conn.execute('''
        CREATE TABLE vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            manufacturer TEXT NOT NULL,
            model TEXT NOT NULL,
            daily_rental_rate REAL NOT NULL,
            number_of_seats INTEGER NOT NULL,
            branch_id INTEGER NOT NULL,
            FOREIGN KEY (branch_id) REFERENCES branches (branch_id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            customer_name TEXT NOT NULL,
            cost REAL NOT NULL,
            branch_id INTEGER NOT NULL,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id),
            FOREIGN KEY (branch_id) REFERENCES branches (branch_id)
        )
    ''')
    
    
    conn.commit()
    conn.close()


def insert_sample_data():
    """Insert sample data into the database."""
    # First reset the database completely
    delete_data()
    
    conn = get_db_connection()
    
    # Insert sample branches first
    branches = [
        (1, 'Downtown Branch', '123 Main Street, City Center'),
        (2, 'Airport Branch', '456 Airport Drive, Terminal 2'),
        (3, 'Suburban Branch', '789 Oak Avenue, Suburbia Mall')
    ]
    
    conn.executemany('''
        INSERT INTO branches (branch_id, branch_name, address)
        VALUES (?, ?, ?)
    ''', branches)

    # Insert sample vehicles
    vehicles = [
        (1, 'Small', 'Ford', 'Courier', 55.00, 8, 1),
        (2, 'Medium', 'Ford', 'Transit', 85.00, 2, 2),
        (3, 'Large', 'Ford', 'Jumbo', 95.00, 12, 1)
    ]
    
    conn.executemany('''
        INSERT INTO vehicles (id, category, manufacturer, model, daily_rental_rate, number_of_seats, branch_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', vehicles)
    
    # Insert sample bookings
    bookings = [
        (1, 1, '2024-08-15', '2024-08-20', 'John Smith', 375.00, 1),
        (2, 2, '2024-08-18', '2024-08-22', 'Jane Doe', 220.00, 2),
        (3, 3, '2024-08-25', '2024-08-30', 'Bob Johnson', 475.00, 1)
    ]
    
    conn.executemany('''
        INSERT INTO bookings (booking_id, vehicle_id, start_date, end_date, customer_name, cost, branch_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', bookings)
    
    
    conn.commit()
    conn.close()