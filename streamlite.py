import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import sys, os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(__file__))

from backend.predict import (
    get_today_rainfall,
    get_danger_alerts,
    get_district_summary,
    predict_rainfall,
    classify_rainfall,
    get_full_summary,
)
from backend.database import init_schema
init_schema()

st.set_page_config(
    page_title="WMD Irrigation Monitor",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# basic styling — keeping it clean but not too polished
st.markdown("""
<style>
    .main, .stApp { background: #f8f6f2; }

    .metric-card {
        background: white;
        border: 1px solid #e0dcd5;
        border-radius: 6px;
        padding: 16px 20px;
        margin-bottom: 10px;
    }
    .metric-val { font-size: 28px; font-weight: 600; color: #1a1a18; }
    .metric-lbl {
        font-size: 11px;
        color: #888880;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .alert-box {
        background: #fff5f3;
        border: 1px solid #f0b0a0;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        font-size: 13px;
    }

    /* chat bubbles */
    .chat-msg-ai {
        background: white;
        border: 1px solid #e0dcd5;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 13px;
        line-height: 1.6;
    }
    .chat-msg-user {
        background: #1a1a18;
        color: #e8e4dc;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 13px;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)


# ── sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌧️ WMD Monitor")
    st.markdown("**West Bengal I&WD**")
    st.markdown("Irrigation Data Management System")
    st.markdown("---")

    page = st.radio("Navigate", [
        "📊 Dashboard",
        "🤖 AI Chatbot",
        "🚨 Danger Alerts",
        "🔮 Predict Rainfall",
        "📈 Trends",
    ])

    st.markdown("---")
    st.markdown("**Built by:** Amrapali")
    st.markdown("**B.Tech CSE | 2026**")


# cache helpers — 5 min TTL is fine for this data
@st.cache_data(ttl=300)
def load_summary():
    try:
        return get_full_summary()
    except Exception:
        return None


@st.cache_data(ttl=300)
def load_rainfall(d=None):
    try:
        return get_today_rainfall(d)
    except Exception:
        return pd.DataFrame(), None


@st.cache_data(ttl=300)
def load_alerts(d=None):
    try:
        return get_danger_alerts(d)
    except Exception:
        return pd.DataFrame(), None


@st.cache_data(ttl=300)
def load_district(d=None):
    try:
        return get_district_summary(d)
    except Exception:
        return pd.DataFrame(), None


# ════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 WMD Daily Flood Report Dashboard")

    summary = load_summary()

    if not summary:
        st.warning("Could not connect to database. Please run `python backend/load_data.py` first.")
        st.stop()

    st.markdown(f"**Latest data date:** {summary['date']}")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Stations", summary["total_stations"])
    col2.metric("Total Rainfall", f"{summary['total_rainfall_mm']} mm")
    col3.metric("Max Station Rainfall", f"{summary['max_rainfall_mm']} mm")
    col4.metric(
        "🚨 Danger Alerts",
        summary["danger_alerts"],
        delta="Active" if summary["danger_alerts"] > 0 else "Clear",
        delta_color="inverse",
    )

    st.markdown("---")

    if summary.get("district_summary"):
        dist_df = pd.DataFrame(summary["district_summary"])
        left, right = st.columns(2)

        with left:
            st.subheader("Rainfall by District")
            fig = px.bar(
                dist_df, x="district", y="total_mm",
                color="total_mm",
                color_continuous_scale="Blues",
                labels={"total_mm": "Total Rainfall (mm)", "district": "District"},
            )
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with right:
            st.subheader("Top 10 Rainfall Stations")
            if summary.get("top_stations"):
                top_df = pd.DataFrame(summary["top_stations"])
                fig2 = px.bar(
                    top_df, x="rainfall_mm", y="location",
                    orientation="h",
                    color="rainfall_mm",
                    color_continuous_scale="Teal",
                    labels={"rainfall_mm": "Rainfall (mm)", "location": "Station"},
                )
                fig2.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

    if summary.get("alerts"):
        st.subheader("🚨 Active Danger Level Alerts")
        for a in summary["alerts"]:
            st.markdown(f"""
            <div class="alert-box">
            🔴 <b>{a['river']}</b> @ {a['gauge_station']} —
            Level: <b>{a['gauge_level_m']}m</b> |
            Danger: {a['danger_level']}m |
            Trend: {a['trend']}
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# AI CHATBOT
# ════════════════════════════════════════════════════════════
elif page == "🤖 AI Chatbot":
    st.title("🤖 WMD AI Rainfall Assistant")
    st.markdown("Ask me anything about today's rainfall, river levels, or danger alerts.")

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                "Hello! I am the WMD Rainfall Assistant. "
                "Ask me about today's rainfall, river gauge levels, or danger alerts "
                "across West Bengal districts."
            ),
        }]

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown(
                f'<div class="chat-msg-ai">🌧️ {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-msg-user">👤 {msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    # quick-fire buttons for common queries
    st.markdown("**Quick questions:**")
    c1, c2, c3 = st.columns(3)
    if c1.button("🌧️ Rainfall today"):
        st.session_state.quick = "How much rainfall happened today?"
    if c2.button("🚨 Danger alerts"):
        st.session_state.quick = "Are there any danger level alerts?"
    if c3.button("📊 District summary"):
        st.session_state.quick = "Give me district-wise rainfall summary"

    user_input = st.chat_input("Ask about rainfall, river levels, danger alerts...")
    if hasattr(st.session_state, "quick"):
        user_input = st.session_state.quick
        del st.session_state.quick

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        summary = load_summary()
        if summary:
            ctx = f"""Latest date: {summary['date']}
Total stations reporting: {summary['total_stations']}
Total rainfall: {summary['total_rainfall_mm']}mm
Max rainfall: {summary['max_rainfall_mm']}mm at {summary['max_station']} ({summary['max_district']})
Danger alerts: {summary['danger_alerts']}
Top stations: {summary['top_stations'][:5]}
Danger alerts detail: {summary['alerts']}
District summary: {summary['district_summary']}"""
        else:
            ctx = "No data available. Database connection failed."

        try:
            import anthropic
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            client = anthropic.Anthropic(api_key=api_key)

            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=f"""You are WMD Rainfall Assistant for West Bengal I&WD.
Answer questions about rainfall, river gauge levels and flood danger alerts.
Use this data context to answer accurately:
{ctx}
Be concise and factual. Use mm for rainfall. Flag danger alerts clearly.""",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )
            reply = resp.content[0].text

        except Exception as e:
            # fallback when API isn't available
            if summary:
                reply = (
                    f"Based on the latest data ({summary['date']}):\n"
                    f"• Total rainfall recorded: {summary['total_rainfall_mm']} mm "
                    f"across {summary['total_stations']} stations\n"
                    f"• Highest rainfall: {summary['max_rainfall_mm']} mm at "
                    f"{summary['max_station']} ({summary['max_district']})\n"
                    f"• Active danger alerts: {summary['danger_alerts']}\n"
                    f"• IMD Category: {classify_rainfall(summary['max_rainfall_mm'])}"
                )
            else:
                reply = "Database not connected. Please run load_data.py first."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


# ════════════════════════════════════════════════════════════
# DANGER ALERTS
# ════════════════════════════════════════════════════════════
elif page == "🚨 Danger Alerts":
    st.title("🚨 River Gauge Danger Alerts")

    alert_df, alert_date = load_alerts()

    if alert_df is not None and len(alert_df) > 0:
        st.error(f"⚠️ {len(alert_df)} danger level breaches as of {alert_date}")
        st.dataframe(alert_df, use_container_width=True)

        fig = px.bar(
            alert_df, x="gauge_station", y="gauge_level_m",
            color="exceeded_by_m",
            color_continuous_scale="Reds",
            title="Gauge Level vs Danger Level",
            labels={"gauge_level_m": "Gauge Level (m)"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No danger level breaches found for the latest date.")


# ════════════════════════════════════════════════════════════
# RAINFALL PREDICTION
# ════════════════════════════════════════════════════════════
elif page == "🔮 Predict Rainfall":
    st.title("🔮 Rainfall Prediction")
    st.markdown("Predict rainfall for any station using the trained ML model.")

    col1, col2 = st.columns(2)
    with col1:
        district  = st.text_input("District", value="Bankura")
        location  = st.text_input("Station / Location", value="Bankura")
        session   = st.selectbox("Session", ["Morning", "Evening"])
    with col2:
        pred_date = st.date_input("Date", value=date.today())

    if st.button("🔮 Predict", type="primary"):
        result = predict_rainfall(district, location, session, pred_date)
        if result is not None:
            category = classify_rainfall(result)
            st.success(f"**Predicted Rainfall: {result} mm**")
            st.info(f"IMD Category: **{category}**")
            # thresholds from IMD classification
            if result >= 115:
                st.error("🚨 Very heavy rainfall! Flood risk high.")
            elif result >= 64:
                st.warning("⚠️ Heavy rainfall expected. Monitor river levels.")
        else:
            st.error("Model not found. Please run `python backend/train_model.py` first.")


# ════════════════════════════════════════════════════════════
# TRENDS
# ════════════════════════════════════════════════════════════
elif page == "📈 Trends":
    st.title("📈 Rainfall & River Trends")

    try:
        from sqlalchemy import create_engine

        db_host     = os.environ.get("DB_HOST", "localhost")
        db_user     = os.environ.get("DB_USER", "root")
        db_password = os.environ.get("DB_PASSWORD", "your_password")
        db_name     = os.environ.get("DB_NAME", "wmd_irrigation")
        db_port     = os.environ.get("DB_PORT", "3306")

        engine = create_engine(
            f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )

        rain_trend = pd.read_sql("""
            SELECT `date`,
                   ROUND(SUM(rainfall_mm), 1) AS total_mm,
                   MAX(rainfall_mm)            AS max_mm,
                   COUNT(*)                    AS stations
            FROM rainfall
            WHERE rainfall_mm IS NOT NULL
            GROUP BY `date`
            ORDER BY `date`
        """, engine)
        rain_trend["date"] = pd.to_datetime(rain_trend["date"])

        st.subheader("Daily Total Rainfall")
        fig = px.line(
            rain_trend, x="date", y="total_mm",
            title="Total Rainfall Across All Stations",
            labels={"total_mm": "Total Rainfall (mm)", "date": "Date"},
        )
        fig.add_bar(x=rain_trend["date"], y=rain_trend["max_mm"],
                    name="Max Station", opacity=0.4)
        st.plotly_chart(fig, use_container_width=True)

        gauge_trend = pd.read_sql("""
            SELECT `date`, river, gauge_station,
                   AVG(gauge_level_m)  AS avg_level,
                   MAX(danger_level)   AS danger_level
            FROM river_gauge
            WHERE gauge_level_m IS NOT NULL
            GROUP BY `date`, river, gauge_station
            ORDER BY `date`
        """, engine)
        gauge_trend["date"] = pd.to_datetime(gauge_trend["date"])

        st.subheader("River Gauge Level Trends")
        rivers = gauge_trend["river"].dropna().unique()
        selected_river = st.selectbox("Select River", rivers)

        filtered = gauge_trend[gauge_trend["river"] == selected_river]
        fig2 = px.line(
            filtered, x="date", y="avg_level",
            color="gauge_station",
            title=f"{selected_river} — Gauge Levels Over Time",
            labels={"avg_level": "Gauge Level (m)"},
        )
        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Database error: {e}")
        st.info("Please run `python backend/load_data.py` first.")