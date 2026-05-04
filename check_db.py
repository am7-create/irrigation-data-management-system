import sqlite3
import os

db_path = 'wmd_irrigation.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check rainfall table
    cur.execute('SELECT COUNT(*) FROM rainfall')
    rain_count = cur.fetchone()[0]
    
    # Check river_gauge table
    cur.execute('SELECT COUNT(*) FROM river_gauge')
    gauge_count = cur.fetchone()[0]
    
    print('✅ Database loaded successfully!')
    print(f'  🌧️  Rainfall records: {rain_count}')
    print(f'  🌊 River gauge records: {gauge_count}')
    
    if rain_count > 0:
        cur.execute('SELECT date, location, rainfall_mm FROM rainfall LIMIT 3')
        print('  📊 Sample rainfall data:')
        for row in cur.fetchall():
            print(f'     {row[0]} - {row[1]}: {row[2]}mm')
    
    if gauge_count > 0:
        cur.execute('SELECT date, river, gauge_level_m FROM river_gauge LIMIT 3')
        print('  📊 Sample river gauge data:')
        for row in cur.fetchall():
            print(f'     {row[0]} - {row[1]}: {row[2]}m')
    
    conn.close()
else:
    print('❌ Database file not found')