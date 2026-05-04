"""
load_data.py
============
Data loading and ingestion utilities for WMD Irrigation System.

Usage:
    python -m backend.load_data
"""

import os
import pandas as pd
from datetime import date
from backend.database import get_db_engine, init_database
from backend.predict import load_sample_data


def main():
    """Initialize database and load sample data."""
    print("🌧️ WMD Irrigation Data Management System - Data Loader")
    print("=" * 60)
    
    print("\n1️⃣  Initializing database schema...")
    if not init_database():
        print("❌ Failed to initialize database")
        print("   Make sure MySQL is running and .env is configured correctly")
        return False
    
    print("\n2️⃣  Loading sample data...")
    if not load_sample_data():
        print("❌ Failed to load sample data")
        return False
    
    print("\n✅ Data loading complete!")
    print("\nNext steps:")
    print("  1. Run: streamlit run load_data.py")
    print("  2. Open: http://localhost:8501")
    print("  3. Enjoy the WMD Dashboard!")
    
    return True


if __name__ == "__main__":
    main()
