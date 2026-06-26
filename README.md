# 🌧️ WMD Irrigation Data Management System

**West Bengal Irrigation & Waterways Department** — Comprehensive flood monitoring and rainfall prediction dashboard with AI chatbot integration.

## 📋 Features

- **📊 Dashboard** — Real-time rainfall metrics, district summaries, and danger alerts
- **🤖 AI Chatbot** — Claude-powered assistant for rainfall and flood queries
- **🚨 Danger Alerts** — River gauge level monitoring and breach notifications
- **🔮 Rainfall Prediction** — ML-based rainfall forecasting
- **📈 Trends** — Historical rainfall and river level analysis

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server (running locally or accessible)


### Step 1: Clone/Extract Project
```bash
cd c:\Users\KIIT0001\Desktop\irrigation_data_management_system
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create or edit `.env` file in the project root:

```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-...your-actual-key-from-console.anthropic.com...

# Database Configuration (MySQL)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=wmd_irrigation
DB_PORT=3306

# Application
DEBUG=False
```

**To get your Anthropic API key:**
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Create API key in account settings
4. Paste it in `.env` file

### Step 4: Set Up MySQL Database

```bash
# Open MySQL command line
mysql -u root -p

# Create database
CREATE DATABASE wmd_irrigation;

# Verify
SHOW DATABASES;
```

### Step 5: Initialize Database & Load Sample Data

```bash
python -m backend.load_data
```

This will:
- Create required tables (rainfall, river_gauge)
- Load sample data for today's date
- Verify database connection

**Expected output:**
```
🌧️ WMD Irrigation Data Management System - Data Loader
============================================================

1️⃣  Initializing database schema...
✅ Database schema initialized

2️⃣  Loading sample data...
✅ Sample data loaded successfully

✅ Data loading complete!
```

---

## 🚀 Running the Application

### Start Streamlit Server
```bash
streamlit run load_data.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

### Access Dashboard
Open browser and go to: **http://localhost:8501**

---

## 📊 Database Schema

### `rainfall` Table
```sql
CREATE TABLE rainfall (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    location VARCHAR(255) NOT NULL,
    district VARCHAR(100) NOT NULL,
    rainfall_mm FLOAT,
    session VARCHAR(50),  -- 'Morning' or 'Evening'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_district (district)
);
```

### `river_gauge` Table
```sql
CREATE TABLE river_gauge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    river VARCHAR(100) NOT NULL,
    gauge_station VARCHAR(255) NOT NULL,
    gauge_level_m FLOAT NOT NULL,
    danger_level FLOAT,
    trend VARCHAR(50),  -- 'Rising', 'Steady', 'Falling'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_river (river)
);
```

---

## 🧪 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'backend'"
**Solution:**
```bash
# Reinstall with dependencies
pip install -r requirements.txt

# Verify backend directory exists
ls backend/
```

### Issue: "MySQL Connection Error"
**Solutions:**
1. Verify MySQL is running:
   ```bash
   mysql -u root -p -e "SELECT 1"
   ```
2. Check `.env` credentials match your MySQL setup
3. Verify database `wmd_irrigation` exists:
   ```bash
   mysql -u root -p -e "SHOW DATABASES LIKE 'wmd%';"
   ```

### Issue: "ANTHROPIC_API_KEY not found"
**Solution:**
1. Verify `.env` file exists in project root
2. Verify ANTHROPIC_API_KEY line is present
3. The AI chatbot will work with limited fallback responses if key is missing

### Issue: "No data appears on Dashboard"
**Solution:**
Run database initialization:
```bash
python -m backend.load_data
```

---

## 📁 Project Structure

```
irrigation_data_management_system/
├── load_data.py              # Main Streamlit app
├── requirements.txt          # Python dependencies
├── .env                      # Configuration (DO NOT COMMIT)
├── README.md                 # This file
└── backend/
    ├── __init__.py
    ├── database.py           # Database connection utilities
    ├── predict.py            # Core prediction & data retrieval
    ├── load_data.py          # Data loader script
    └── train_model.py        # ML model training (placeholder)
```

---

## 🔄 Development Workflow

### Add New Rainfall Data
```python
# backend/predict.py - add to load_sample_data()
# Or insert directly via SQL:
INSERT INTO rainfall (date, location, district, rainfall_mm, session)
VALUES ('2026-05-03', 'City', 'District', 75.5, 'Morning');
```

### Add New River Station
```sql
INSERT INTO river_gauge (date, river, gauge_station, gauge_level_m, danger_level, trend)
VALUES ('2026-05-03', 'River Name', 'Station Name', 42.5, 40.0, 'Rising');
```

### Update AI Chatbot System Prompt
Edit line ~285 in `load_data.py` - modify the `system=` parameter.

---

## 🎯 Next Steps

1. **Load Real Data** — Replace sample data with actual IMD/WBD rainfall records
2. **Train ML Model** — Implement actual rainfall prediction model in `backend/train_model.py`
3. **Production Deployment** — Deploy to cloud service (AWS, GCP, Heroku)
4. **API Integration** — Connect to official IMD/WBD APIs for live data
5. **Mobile App** — Build complementary mobile application

---

## 📞 Support

For issues or questions:
1. Check this README's Troubleshooting section
2. Review error messages in Streamlit terminal
3. Verify database connectivity: `mysql -u root -p -D wmd_irrigation`

---

## 📝 License

Built for **West Bengal Irrigation & Waterways Department**  
**Author:** Amrapali | B.Tech CSE | 2026

---

**Last Updated:** May 3, 2026  
**Version:** 1.0.0
