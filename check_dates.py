#!/usr/bin/env python3
"""Check database dates"""

import sqlite3
import datetime

conn = sqlite3.connect('wmd_irrigation.db')
cursor = conn.cursor()

today = datetime.date.today().isoformat()
print(f'Today: {today}')

cursor.execute('SELECT DISTINCT date FROM rainfall ORDER BY date DESC LIMIT 5')
dates = cursor.fetchall()
print('Available dates in rainfall table:')
for date_row in dates:
    print(f'  {date_row[0]}')

cursor.execute('SELECT COUNT(*) FROM rainfall WHERE date = ?', (today,))
count = cursor.fetchone()[0]
print(f'Records for today: {count}')

conn.close()