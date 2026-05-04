#!/usr/bin/env python3
"""Check rainfall values"""

import sqlite3

conn = sqlite3.connect('wmd_irrigation.db')
cursor = conn.cursor()

cursor.execute('SELECT location, rainfall_mm FROM rainfall WHERE date = "2025-11-07" LIMIT 10')
rows = cursor.fetchall()

print('Sample rainfall data for 2025-11-07:')
for row in rows:
    print(f'  {row[0]}: {row[1]} ({type(row[1])})')

conn.close()