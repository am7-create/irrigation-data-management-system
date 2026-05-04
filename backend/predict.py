"""
predict.py
==========
Core prediction and data retrieval functions for WMD Irrigation System.
"""

import pandas as pd
from datetime import date, datetime, timedelta
from backend.database import get_db_engine
import os

# ── Database Engine ──────────────────────────────────────────
engine = get_db_engine()


# ── Rainfall Classification ──────────────────────────────────
def classify_rainfall(rainfall_mm):
    """
    Classify rainfall according to IMD categories.
    
    Categories:
    - Light: < 15.6 mm
    - Moderate: 15.6 - 64.4 mm
    - Heavy: 64.5 - 115.6 mm
    - Very Heavy: >= 115.6 mm
    """
    if rainfall_mm is None:
        return "Unknown"
    if rainfall_mm < 15.6:
        return "Light"
    elif rainfall_mm < 64.5:
        return "Moderate"
    elif rainfall_mm < 115.6:
        return "Heavy"
    else:
        return "Very Heavy"


def get_today_rainfall(target_date=None):
    """
    Get rainfall data for today (or specified date).
    
    Returns:
        pd.DataFrame: Columns [location, district, rainfall_mm, session]
    """
    if engine is None:
        return pd.DataFrame()
    
    if target_date is None:
        target_date = date.today()
    
    try:
        query = f"""
        SELECT location, district, rainfall_mm, session
        FROM rainfall
        WHERE date = '{target_date}'
        ORDER BY rainfall_mm DESC
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        print(f"Error fetching today's rainfall: {e}")
        return pd.DataFrame()


def get_danger_alerts(target_date=None):
    """
    Get river gauge danger level alerts.
    
    Returns:
        tuple: (DataFrame with columns [gauge_station, river, gauge_level_m, 
                danger_level, exceeded_by_m], alert_date)
    """
    if engine is None:
        return pd.DataFrame(), None
    
    if target_date is None:
        target_date = date.today()
    
    try:
        query = f"""
        SELECT gauge_station, river, gauge_level_m, danger_level,
               ROUND(gauge_level_m - danger_level, 2) AS exceeded_by_m
        FROM river_gauge
        WHERE date = '{target_date}' AND gauge_level_m >= danger_level
        ORDER BY exceeded_by_m DESC
        """
        df = pd.read_sql(query, engine)
        return df, str(target_date)
    except Exception as e:
        print(f"Error fetching danger alerts: {e}")
        return pd.DataFrame(), str(target_date)


def get_district_summary(target_date=None):
    """
    Get district-wise rainfall summary.
    
    Returns:
        list: List of dicts with [district, total_mm, stations, avg_mm]
    """
    if engine is None:
        return []
    
    if target_date is None:
        target_date = date.today()
    
    try:
        query = f"""
        SELECT district,
               ROUND(SUM(rainfall_mm), 1) AS total_mm,
               COUNT(*) AS stations,
               ROUND(AVG(rainfall_mm), 1) AS avg_mm
        FROM rainfall
        WHERE date = '{target_date}' AND rainfall_mm IS NOT NULL
        GROUP BY district
        ORDER BY total_mm DESC
        """
        df = pd.read_sql(query, engine)
        return df.to_dict('records') if len(df) > 0 else []
    except Exception as e:
        print(f"Error fetching district summary: {e}")
        return []


def predict_rainfall(district, location, session, pred_date):
    """
    Predict rainfall for a specific station using ML model.
    
    Args:
        district (str): District name
        location (str): Station/location name
        session (str): "Morning" or "Evening"
        pred_date (date): Prediction date
    
    Returns:
        float: Predicted rainfall in mm, or None if model not found
    """
    try:
        # Simple baseline model - replace with actual ML model
        # This is a placeholder; you would load a trained sklearn/tf model
        import random
        
        # Simulate prediction based on historical patterns
        predicted_rainfall = random.uniform(5, 80)
        return round(predicted_rainfall, 1)
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None


def get_full_summary(target_date=None):
    """
    Get comprehensive summary of current situation.
    
    Returns:
        dict: Complete summary with all metrics
    """
    if engine is None:
        return None
    
    if target_date is None:
        target_date = date.today()
    
    try:
        # Check if data exists for target date, if not use the date with most rainfall data
        date_check = pd.read_sql(f"""
            SELECT COUNT(*) as count FROM rainfall 
            WHERE date = '{target_date}' AND rainfall_mm IS NOT NULL
        """, engine)
        
        if date_check.iloc[0]['count'] == 0:
            # Get date with most rainfall records
            best_date_df = pd.read_sql("""
                SELECT date FROM rainfall 
                WHERE rainfall_mm IS NOT NULL 
                GROUP BY date 
                ORDER BY COUNT(*) DESC, date DESC 
                LIMIT 1
            """, engine)
            if len(best_date_df) > 0:
                target_date = best_date_df.iloc[0]['date']
                print(f"No data for today, using date with most data: {target_date}")
            else:
                return None
        
        # Total rainfall
        rain_df = pd.read_sql(f"""
            SELECT COUNT(*) as total_stations,
                   COALESCE(ROUND(SUM(rainfall_mm), 1), 0) as total_rainfall_mm,
                   COALESCE(ROUND(MAX(rainfall_mm), 1), 0) as max_rainfall_mm,
                   location as max_station,
                   district as max_district
            FROM rainfall
            WHERE date = '{target_date}' AND rainfall_mm IS NOT NULL
            ORDER BY rainfall_mm DESC
            LIMIT 1
        """, engine)
        
        if len(rain_df) == 0:
            return None
        
        # Top stations
        top_df = pd.read_sql(f"""
            SELECT location, rainfall_mm, district
            FROM rainfall
            WHERE date = '{target_date}' AND rainfall_mm IS NOT NULL
            ORDER BY rainfall_mm DESC
            LIMIT 10
        """, engine)
        
        # Danger alerts
        alert_df = pd.read_sql(f"""
            SELECT gauge_station, river, gauge_level_m, danger_level, trend
            FROM river_gauge
            WHERE date = '{target_date}' AND gauge_level_m >= danger_level
        """, engine)
        
        # District summary
        dist_summary = get_district_summary(target_date)
        
        return {
            "date": str(target_date),
            "total_stations": int(rain_df.iloc[0]['total_stations']),
            "total_rainfall_mm": float(rain_df.iloc[0]['total_rainfall_mm']),
            "max_rainfall_mm": float(rain_df.iloc[0]['max_rainfall_mm']),
            "max_station": rain_df.iloc[0]['max_station'],
            "max_district": rain_df.iloc[0]['max_district'],
            "danger_alerts": len(alert_df),
            "top_stations": top_df.to_dict('records'),
            "alerts": alert_df.to_dict('records'),
            "district_summary": dist_summary
        }
    except Exception as e:
        print(f"Error getting full summary: {e}")
        return None


# ── Data Loading ─────────────────────────────────────────────
def load_sample_data():
    """
    Load sample data into database for testing.
    This should be run once after database initialization.
    """
    if engine is None:
        print("Cannot load sample data: database connection failed")
        return False
    
    try:
        from sqlalchemy import text
        today = date.today()
        
        with engine.connect() as conn:
            # Sample rainfall data
            conn.execute(text(f"""
            INSERT INTO rainfall (date, location, district, rainfall_mm, session)
            VALUES 
            ('{today}', 'Kolkata', 'Kolkata', 45.2, 'Morning'),
            ('{today}', 'Darjeeling', 'Darjeeling', 120.5, 'Morning'),
            ('{today}', 'Bankura', 'Bankura', 65.3, 'Evening'),
            ('{today}', 'Siliguri', 'Darjeeling', 95.1, 'Morning'),
            ('{today}', 'Cooch Behar', 'Cooch Behar', 110.8, 'Morning'),
            ('{today}', 'Purulia', 'Purulia', 25.5, 'Evening')
            """))
            
            # Sample river gauge data
            conn.execute(text(f"""
            INSERT INTO river_gauge (date, river, gauge_station, gauge_level_m, danger_level, trend)
            VALUES 
            ('{today}', 'Brahmaputra', 'Gauhati', 58.5, 57.0, 'Rising'),
            ('{today}', 'Ganges', 'Varanasi', 82.1, 80.5, 'Steady'),
            ('{today}', 'Teesta', 'Sevoke', 45.2, 43.0, 'Rising'),
            ('{today}', 'Mahananda', 'Mahananda Bridge', 28.5, 28.0, 'Rising')
            """))
            
            conn.commit()
            print("✅ Sample data loaded successfully")
            return True
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return False
