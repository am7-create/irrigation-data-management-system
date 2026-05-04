#!/usr/bin/env python3
"""Check for non-null rainfall values"""

import sqlite3

conn = sqlite3.connect('wmd_irrigation.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM rainfall WHERE rainfall_mm IS NOT NULL')
count = cursor.fetchone()[0]
print(f'Records with non-null rainfall: {count}')

if count > 0:
    cursor.execute('SELECT location, rainfall_mm FROM rainfall WHERE rainfall_mm IS NOT NULL LIMIT 5')
    rows = cursor.fetchall()
    print('Sample non-null rainfall:')
    for row in rows:
        print(f'  {row[0]}: {row[1]}')

conn.close()