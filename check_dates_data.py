#!/usr/bin/env python3
"""Check dates with most rainfall data"""

import sqlite3

conn = sqlite3.connect('wmd_irrigation.db')
cursor = conn.cursor()

cursor.execute('SELECT date, COUNT(*) as count FROM rainfall WHERE rainfall_mm IS NOT NULL GROUP BY date ORDER BY count DESC LIMIT 5')
rows = cursor.fetchall()

print('Dates with most rainfall records:')
for row in rows:
    print(f'  {row[0]}: {row[1]} records')

conn.close()