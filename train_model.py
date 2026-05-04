"""
BACKEND — train_model.py
========================
Trains a rainfall prediction model using historical WMD data.

Usage:
    python backend/train_model.py
"""

import pandas as pd
import numpy as np
import pickle
import os
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
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


def load_data(engine):
    df = pd.read_sql("""
        SELECT `date`, session, district, location,
               gauge_type, rainfall_mm, cum_rainfall_mm
        FROM rainfall
        WHERE rainfall_mm IS NOT NULL
        ORDER BY `date`, location
    """, engine)
    return df


def engineer_features(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"]    = df["date"].dt.month
    df["day"]      = df["date"].dt.day
    df["day_of_year"] = df["date"].dt.dayofyear
    df["is_morning"] = (df["session"] == "Morning").astype(int)

    # Monsoon season flag
    df["is_monsoon"] = df["month"].isin([6,7,8,9]).astype(int)

    return df


def encode_features(df):
    encoders = {}
    for col in ["district", "location", "gauge_type"]:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col].fillna("Unknown"))
        encoders[col] = le
    return df, encoders


def train(df, encoders):
    features = [
        "month", "day", "day_of_year", "is_morning", "is_monsoon",
        "district_enc", "location_enc", "gauge_type_enc",
        "cum_rainfall_mm"
    ]
    df = df.dropna(subset=features + ["rainfall_mm"])
    X = df[features]
    y = df["rainfall_mm"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "Linear Regression": LinearRegression()
    }

    best_model = None
    best_r2 = -999
    best_name = ""

    print("\nModel Training Results:")
    print("-" * 45)
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2  = r2_score(y_test, preds)
        print(f"  {name:25s} MAE={mae:.2f}mm  R²={r2:.3f}")
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            best_name = name

    print(f"\n✓ Best model: {best_name} (R²={best_r2:.3f})")
    return best_model, features


def save_artifacts(model, encoders, features):
    os.makedirs("outputs", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "features": features}, f)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoders, f)
    print(f"✓ Model saved to: {MODEL_PATH}")
    print(f"✓ Encoders saved to: {ENCODER_PATH}")


def main():
    print("Loading data from MySQL...")
    engine = get_engine()
    df = load_data(engine)
    print(f"  Loaded {len(df)} records")

    print("Engineering features...")
    df = engineer_features(df)
    df, encoders = encode_features(df)

    print("Training models...")
    model, features = train(df, encoders)

    save_artifacts(model, encoders, features)
    print("\n✓ Training complete!")


if __name__ == "__main__":
    main()