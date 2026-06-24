"""
backend/database.py
===================
Database connection and utilities for WMD Irrigation Data Management System.
Uses SQLite — no server, no credentials required.
"""

import os
import sqlite3
from sqlalchemy import create_engine, text

# Path to SQLite database file (project root)
DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'wmd_irrigation.db')
)


# ── Raw sqlite3 connection (fast, lightweight) ─────────────────────────────

def get_connection():
    """Return a sqlite3 connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def test_connection():
    """Test the SQLite connection. Returns True/False."""
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        print(f"✅ SQLite connection OK → {DB_PATH}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


# ── SQLAlchemy engine (for pandas read_sql) ────────────────────────────────

def get_engine():
    """Return a SQLAlchemy engine for pandas read_sql() calls."""
    return create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False}
    )


# Alias for backward compatibility with old code that calls get_db_engine()
def get_db_engine():
    return get_engine()


# ── Schema initialisation ──────────────────────────────────────────────────

def init_schema():
    """
    Create all tables if they don't exist.
    Safe to call multiple times. Includes all columns from both versions.
    """
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS rainfall (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            date               DATE    NOT NULL,
            session            TEXT,
            location           TEXT    NOT NULL,
            district           TEXT    NOT NULL,
            river_sub_basin    TEXT,
            gauge_type         TEXT,
            rainfall_mm        REAL,
            cum_rainfall_mm    REAL,
            normal_annual_mm   REAL,
            division           TEXT,
            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_rainfall_date     ON rainfall(date);
        CREATE INDEX IF NOT EXISTS idx_rainfall_district ON rainfall(district);
        CREATE INDEX IF NOT EXISTS idx_rainfall_location ON rainfall(location);

        CREATE TABLE IF NOT EXISTS river_gauge (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            date                 DATE    NOT NULL,
            session              TEXT,
            river                TEXT    NOT NULL,
            gauge_station        TEXT    NOT NULL,
            district             TEXT,
            gauge_level_m        REAL    NOT NULL,
            danger_level         REAL,
            extreme_danger_level REAL,
            trend                TEXT,
            division             TEXT,
            created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_gauge_date    ON river_gauge(date);
        CREATE INDEX IF NOT EXISTS idx_gauge_river   ON river_gauge(river);
        CREATE INDEX IF NOT EXISTS idx_gauge_station ON river_gauge(gauge_station);
    """)
    conn.commit()
    conn.close()
    print(f"✅ SQLite schema initialised → {DB_PATH}")


# Alias for backward compatibility with old code that calls init_database()
def init_database():
    return init_schema()


if __name__ == "__main__":
    test_connection()
    init_schema()