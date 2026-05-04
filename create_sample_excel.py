import pandas as pd
from pathlib import Path

rain = pd.DataFrame([
    [None, 'Basin1', 'District1', 'Station1', 'RainType', 12.5, 20.0, 100.0, 'Division1'],
    [None, None, 'District1', 'Station2', 'RainType', 0.0, 20.0, 100.0, 'Division1']
])
water = pd.DataFrame([
    [1, 'River1', 'Gauge1', 'District1', 10.2, 'Rising', 9.5, 12.0, 'Division1'],
    [2, 'River2', 'Gauge2', 'District1', 8.0, 'Steady', 7.0, 11.0, 'Division1']
])

with pd.ExcelWriter('sample_test.xlsx', engine='openpyxl') as writer:
    rain.to_excel(writer, sheet_name='Rainfall', header=False, index=False)
    water.to_excel(writer, sheet_name='River Gauge', header=False, index=False)

print(Path('sample_test.xlsx').absolute())