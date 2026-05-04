#!/usr/bin/env python3
"""Check raw database values"""

import sqlite3

conn = sqlite3.connect('wmd_irrigation.db')
cursor = conn.cursor()

cursor.execute('SELECT location, rainfall_mm, typeof(rainfall_mm) FROM rainfall WHERE date = "2025-11-07" LIMIT 5')
rows = cursor.fetchall()

print('Raw database values:')
for row in rows:
    print(f'  {row[0]}: {repr(row[1])} (type: {row[2]})')

conn.close()