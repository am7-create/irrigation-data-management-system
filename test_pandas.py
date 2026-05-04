#!/usr/bin/env python3
"""Test pandas None handling in SQLite"""

import pandas as pd
import sqlite3

# Create test data with None
data = [
    {'date': '2025-01-01', 'location': 'Test', 'rainfall_mm': None},
    {'date': '2025-01-01', 'location': 'Test2', 'rainfall_mm': 5.0}
]

df = pd.DataFrame(data)
print('DataFrame:')
print(df)
print(f'rainfall_mm dtypes: {df["rainfall_mm"].dtype}')

# Save to SQLite
conn = sqlite3.connect('test.db')
df.to_sql('test_rainfall', conn, if_exists='replace', index=False)

# Read back
result = pd.read_sql('SELECT * FROM test_rainfall', conn)
print('\nRead back from SQLite:')
print(result)
print(f'rainfall_mm dtypes: {result["rainfall_mm"].dtype}')

conn.close()