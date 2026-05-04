"""
BACKEND — predict.py
====================
Rainfall prediction functions used by the Streamlit app and chatbot.

Usage:
    from backend.predict import predict_rainfall, get_today_summary
"""

import pickle
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, date
import warnings
warnings.filterwarnings("ignore")

# ── CONFIG ───────────────────────────────────────────────────
MYSQL_USER     = "root"
MYSQL_PASSWORD = "Amrahazra7890"
MYSQL_HOST     = "localhost"
MYSQL_DATABASE = "wmd_irrigation"
MODEL_PATH     = "outputs/rainfall_model.pkl"
ENCODER_PATH   = "outputs/label_encoders.pkl"
# ────────────────────────────────────────────────────────────


def get_engine():
    return create_engine(
        f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
    )


def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

def load_encoders():
    with open(ENCODER_PATH, "rb") as f:
        return pickle.load(f)


def get_today_rainfall(target_date=None):
    """Get actual rainfall for a specific date from database."""
    engine = get_engine()
    if target_date is None:
        result = pd.read_sql("SELECT MAX(`date`) AS d FROM rainfall", engine)
        target_date = result["d"][0]

    df = pd.read_sql(f"""
        SELECT `date`, session, district, location,
               rainfall_mm, cum_rainfall_mm, division
        FROM rainfall
        WHERE `date` = '{target_date}'
          AND rainfall_mm IS NOT NULL
        ORDER BY district, location
    """, engine)
    return df, target_date


def get_danger_alerts(target_date=None):
    """Get river gauge danger alerts for a specific date."""
    engine = get_engine()
    if target_date is None:
        result = pd.read_sql("SELECT MAX(`date`) AS d FROM river_gauge", engine)
        target_date = result["d"][0]

    df = pd.read_sql(f"""
        SELECT `date`, session, river, gauge_station,
               district, gauge_level_m, trend,
               danger_level, extreme_danger_level,
               ROUND(gauge_level_m - danger_level, 3) AS exceeded_by_m
        FROM river_gauge
        WHERE `date` = '{target_date}'
          AND gauge_level_m >= danger_level
          AND gauge_level_m IS NOT NULL
          AND danger_level IS NOT NULL
        ORDER BY exceeded_by_m DESC
    """, engine)
    return df, target_date


def get_district_summary(target_date=None):
    """District-wise rainfall summary."""
    engine = get_engine()
    if target_date is None:
        result = pd.read_sql("SELECT MAX(`date`) AS d FROM rainfall", engine)
        target_date = result["d"][0]

    df = pd.read_sql(f"""
        SELECT district,
               COUNT(*) AS stations,
               ROUND(SUM(rainfall_mm), 1) AS total_mm,
               ROUND(AVG(rainfall_mm), 2) AS avg_mm,
               MAX(rainfall_mm) AS max_mm
        FROM rainfall
        WHERE `date` = '{target_date}'
          AND rainfall_mm IS NOT NULL
        GROUP BY district
        ORDER BY total_mm DESC
    """, engine)
    return df, target_date


def predict_rainfall(district, location, session, target_date=None):
    """Predict rainfall for a location using trained ML model."""
    try:
        artifact = load_model()
        encoders = load_encoders()
        model    = artifact["model"]
        features = artifact["features"]

        if target_date is None:
            target_date = date.today()
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        d = target_date
        row = {
            "month": d.month,
            "day": d.day,
            "day_of_year": d.timetuple().tm_yday,
            "is_morning": 1 if session == "Morning" else 0,
            "is_monsoon": 1 if d.month in [6,7,8,9] else 0,
            "cum_rainfall_mm": 0,
        }

        for col in ["district", "location", "gauge_type"]:
            le = encoders.get(col)
            val = district if col == "district" else location if col == "location" else "ORG"
            try:
                row[col + "_enc"] = le.transform([val])[0]
            except:
                row[col + "_enc"] = 0

        X = pd.DataFrame([row])[features]
        pred = model.predict(X)[0]
        return max(0, round(pred, 2))

    except Exception as e:
        return None


def classify_rainfall(mm):
    """IMD rainfall classification."""
    if mm is None: return "No data"
    if mm == 0:    return "No Rainfall"
    if mm < 15:    return "Light"
    if mm < 64:    return "Moderate"
    if mm < 115:   return "Heavy"
    if mm < 204:   return "Very Heavy"
    return "Extremely Heavy"


def get_full_summary(target_date=None):
    """Full summary for chatbot context."""
    rain_df, rd  = get_today_rainfall(target_date)
    alert_df, _  = get_danger_alerts(target_date)
    dist_df, _   = get_district_summary(target_date)

    summary = {
        "date": str(rd),
        "total_stations": len(rain_df),
        "total_rainfall_mm": round(rain_df["rainfall_mm"].sum(), 1) if len(rain_df) else 0,
        "max_rainfall_mm": round(rain_df["rainfall_mm"].max(), 1) if len(rain_df) else 0,
        "max_station": rain_df.loc[rain_df["rainfall_mm"].idxmax(), "location"] if len(rain_df) else "N/A",
        "max_district": rain_df.loc[rain_df["rainfall_mm"].idxmax(), "district"] if len(rain_df) else "N/A",
        "danger_alerts": len(alert_df),
        "district_summary": dist_df.to_dict("records") if len(dist_df) else [],
        "top_stations": rain_df.nlargest(10, "rainfall_mm")[
            ["location","district","rainfall_mm","session"]
        ].to_dict("records") if len(rain_df) else [],
        "alerts": alert_df[
            ["river","gauge_station","gauge_level_m","danger_level","trend"]
        ].to_dict("records") if len(alert_df) else [],
    }
    return summary