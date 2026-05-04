## 🚀 QUICK START GUIDE

### 1. Install Python packages
```bash
pip install -r requirements.txt
```

### 2. Create `.env` file with your credentials
```
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=wmd_irrigation
DB_PORT=3306
```

### 3. Create MySQL Database
```bash
mysql -u root -p
> CREATE DATABASE wmd_irrigation;
> EXIT;
```

### 4. Load Sample Data
```bash
python -m backend.load_data
```

### 5. Run Application
```bash
streamlit run load_data.py
```

### 6. Open in Browser
Visit: http://localhost:8501

---

## ⚡ Common Issues

**"No module named 'backend'"**
- Run: `pip install -r requirements.txt`

**"MySQL Connection Error"**
- Verify MySQL is running
- Check `.env` credentials are correct

**"No data on dashboard"**
- Run: `python -m backend.load_data`

**"AI Chatbot not working"**
- Add valid ANTHROPIC_API_KEY to `.env`
- Get key from: https://console.anthropic.com/

---

See README.md for detailed setup instructions.
