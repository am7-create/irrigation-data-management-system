import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# district coordinates for West Bengal
DISTRICTS = {
    "Kolkata":      (22.5726, 88.3639),
    "Bankura":      (23.2324, 87.0753),
    "Darjeeling":   (27.0360, 88.2627),
    "Murshidabad":  (24.1800, 88.2700),
    "Hooghly":      (22.9000, 88.3900),
    "Bardhaman":    (23.2324, 87.8615),
    "Malda":        (25.0108, 88.1418),
    "Nadia":        (23.4700, 88.5600),
    "Howrah":       (22.5958, 88.2636),
    "Jalpaiguri":   (26.5449, 88.7179),
}

def get_forecast(district="Kolkata"):
    lat, lon = DISTRICTS.get(district, (22.5726, 88.3639))

    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=3, backoff_factor=0.2)
    om = openmeteo_requests.Client(session=retry_session)

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["precipitation_sum", "precipitation_probability_max",
                  "temperature_2m_max", "temperature_2m_min"],
        "timezone": "Asia/Kolkata",
        "forecast_days": 7,
    }

    try:
        responses = om.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
        r = responses[0].Daily()

        dates = pd.date_range(
            start=pd.to_datetime(r.Time(), unit="s", utc=True).tz_convert("Asia/Kolkata"),
            periods=r.Variables(0).ValuesAsNumpy().shape[0],
            freq="D"
        )

        df = pd.DataFrame({
            "date":           dates,
            "rainfall_mm":    r.Variables(0).ValuesAsNumpy().round(1),
            "rain_prob_%":    r.Variables(1).ValuesAsNumpy().round(0).astype(int),
            "temp_max_c":     r.Variables(2).ValuesAsNumpy().round(1),
            "temp_min_c":     r.Variables(3).ValuesAsNumpy().round(1),
        })

        # flood risk tag
        def risk(mm):
            if mm >= 115: return "🔴 Very Heavy"
            elif mm >= 64: return "🟠 Heavy"
            elif mm >= 15: return "🟡 Moderate"
            else:          return "🟢 Low"

        df["flood_risk"] = df["rainfall_mm"].apply(risk)
        return df, district

    except Exception as e:
        print(f"Forecast error: {e}")
        return None, district


def get_all_districts_forecast():
    """Summary forecast for all districts — used for the map/overview."""
    results = []
    for dist in DISTRICTS:
        df, _ = get_forecast(dist)
        if df is not None:
            results.append({
                "district":       dist,
                "total_7day_mm":  df["rainfall_mm"].sum().round(1),
                "max_daily_mm":   df["rainfall_mm"].max(),
                "high_risk_days": int((df["rainfall_mm"] >= 64).sum()),
                "flood_risk":     df["flood_risk"].iloc[df["rainfall_mm"].argmax()],
            })
    return pd.DataFrame(results)