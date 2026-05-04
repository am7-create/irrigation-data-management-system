"""
database.py
===========
Database connection and utilities for WMD Irrigation System.
"""

import os
import sqlite3
from sqlalchemy import create_engine

def get_db_engine():
    """Create and return SQLAlchemy database engine."""
    # Use SQLite instead of MySQL for simplicity
    db_path = os.path.join(os.path.dirname(__file__), '..', 'wmd_irrigation.db')
    connection_string = f"sqlite:///{db_path}"
    
    try:
        engine = create_engine(connection_string)
        # Test connection
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database with required schema."""
    engine = get_db_engine()
    if engine is None:
        print("Cannot initialize database: connection failed")
        return False
    
    try:
        # Create rainfall table
        with engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text("""
            CREATE TABLE IF NOT EXISTS rainfall (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, session TEXT,
                river_sub_basin TEXT, district TEXT,
                location TEXT, gauge_type TEXT,
                rainfall_mm REAL, cum_rainfall_mm REAL,
                normal_annual_mm REAL, division TEXT
            )
            """))
            
            # Create river_gauge table
            conn.execute(__import__('sqlalchemy').text("""
            CREATE TABLE IF NOT EXISTS river_gauge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, session TEXT,
                river TEXT, gauge_station TEXT,
                district TEXT, gauge_level_m REAL,
                trend TEXT, danger_level REAL,
                extreme_danger_level REAL, division TEXT
            )
            """))
            
            conn.commit()
            print("✅ Database schema initialized")
            return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False
