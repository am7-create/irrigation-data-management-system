"""
BACKEND — load_data.py
======================
Reads all WMD Morning/Evening xlsx files and loads into SQLite.

Usage:
    python loaddata.py
"""

import os
import re
import glob
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

# ── CONFIG — SQLite database path ───────────────────────────
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "wmd_irrigation.db")

DATA_FOLDER = r"C:\Users\KIIT0001\Desktop\irrigation data management system\RAINFALL RIVER GAUGE 2025 WMD\RAINFALL RIVER GAUGE 2025 WMD"
# ────────────────────────────────────────────────────────────


def get_engine():
    return create_engine(f"sqlite:///{SQLITE_DB_PATH}")


def parse_date(filepath):
    m = re.search(r"(\d{2})[.\-_](\d{2})[.\-_](\d{4})", filepath)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else None


def get_session(filepath):
    """Extract session from filepath (check directory name)"""
    path_lower = filepath.lower()
    if "morning" in path_lower: 
        return "Morning"
    if "evening" in path_lower: 
        return "Evening"
    return "Unknown"


def safe_float(v):
    try:
        return float(v) if str(v).strip() not in ["nan","NaN","","None"] else None
    except:
        return None


def safe_str(v):
    s = str(v).strip()
    return None if s in ["nan","NaN","None",""] else s


def extract_rainfall(filepath, date, session):
    records = []
    try:
        df = pd.read_excel(filepath, sheet_name="Rainfall", header=None)
        basin = district = None
        for _, row in df.iloc[4:].iterrows():
            vals = list(row)
            b = safe_str(vals[1]); d = safe_str(vals[2])
            loc = safe_str(vals[3]); gtype = safe_str(vals[4])
            if b: basin = b
            if d: district = d
            if gtype and loc:
                records.append({
                    "date": date, "session": session,
                    "river_sub_basin": basin, "district": district,
                    "location": loc, "gauge_type": gtype,
                    "rainfall_mm": safe_float(vals[5]),
                    "cum_rainfall_mm": safe_float(vals[6]),
                    "normal_annual_mm": safe_float(vals[7]),
                    "division": safe_str(vals[8])
                })
    except Exception as e:
        print(f"  Rainfall error: {e}")
    return records


def extract_gauge(filepath, date, session):
    records = []
    try:
        df = pd.read_excel(filepath, sheet_name="River Gauge", header=None)
        for _, row in df.iloc[3:].iterrows():
            vals = list(row)
            sl = safe_str(vals[0])
            if not (sl and sl.isdigit()): continue
            records.append({
                "date": date, "session": session,
                "river": safe_str(vals[1]),
                "gauge_station": safe_str(vals[2]),
                "district": safe_str(vals[3]),
                "gauge_level_m": safe_float(vals[4]),
                "trend": safe_str(vals[5]),
                "danger_level": safe_float(vals[6]),
                "extreme_danger_level": safe_float(vals[7]),
                "division": safe_str(vals[8])
            })
    except Exception as e:
        print(f"  Gauge error: {e}")
    return records


def create_database():
    """SQLite database is created automatically when connecting"""
    print(f"[OK] SQLite database ready: {SQLITE_DB_PATH}")


def create_tables(engine):
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
    print("[OK] Tables ready")


def load_all():
    print("🌧️ WMD Data Loader - Loading Excel files into SQLite")
    print("=" * 60)
    
    create_database()
    engine = get_engine()
    create_tables(engine)

    # Clear old data
    with engine.connect() as conn:
        conn.execute(__import__('sqlalchemy').text("DELETE FROM rainfall"))
        conn.execute(__import__('sqlalchemy').text("DELETE FROM river_gauge"))
        conn.commit()
    print("[OK] Cleared existing data")

    # Find all xlsx files
    all_files = glob.glob(os.path.join(DATA_FOLDER, "**", "*.xlsx"), recursive=True)
    all_files = [f for f in all_files if not os.path.basename(f).startswith("~$")]
    print(f"Found {len(all_files)} Excel files to process")

    rain_all = []
    gauge_all = []

    for i, f in enumerate(all_files, 1):
        date = parse_date(f)
        session = get_session(f)
        if not date: 
            print(f"  [!] Skipping {os.path.basename(f)} - no date found")
            continue
        
        print(f"  [{i}/{len(all_files)}] Reading: {os.path.basename(f)}")
        print(f"      Date: {date}, Session: {session}")
        
        rain_records = extract_rainfall(f, date, session)
        gauge_records = extract_gauge(f, date, session)
        
        rain_all.extend(rain_records)
        gauge_all.extend(gauge_records)
        
        print(f"      Rainfall records: {len(rain_records)}, Gauge records: {len(gauge_records)}")

    # Save to SQLite
    print(f"\nSaving data to database...")
    if rain_all:
        df_rain = pd.DataFrame(rain_all)
        df_rain.to_sql("rainfall", engine, if_exists="append", index=False)
        print(f"  [+] Rainfall: {len(rain_all)} records saved")
    else:
        print("  [!] No rainfall data found")
        
    if gauge_all:
        df_gauge = pd.DataFrame(gauge_all)
        df_gauge.to_sql("river_gauge", engine, if_exists="append", index=False)
        print(f"  [+] River gauge: {len(gauge_all)} records saved")
    else:
        print("  [!] No river gauge data found")

    print(f"\n[DONE] Data loading complete!")
    print(f"Total records loaded:")
    print(f"  Rainfall: {len(rain_all)}")
    print(f"  River gauge: {len(gauge_all)}")
    print(f"  Database: {SQLITE_DB_PATH}")
    
    print(f"\nYour Streamlit dashboard should now show real data!")
    print(f"Visit: http://localhost:8501")