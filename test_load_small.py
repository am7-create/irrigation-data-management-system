import loaddata
import pandas as pd

# Test loading just a few files
DATA_FOLDER = loaddata.DATA_FOLDER
files = loaddata.glob.glob(loaddata.os.path.join(DATA_FOLDER, '**', '*.xlsx'), recursive=True)
files = [f for f in files if not loaddata.os.path.basename(f).startswith('~$')]

print(f'Found {len(files)} files, testing with first 3...')

# Initialize database
loaddata.create_database()
engine = loaddata.get_engine()
loaddata.create_tables(engine)

# Clear existing data
with engine.connect() as conn:
    conn.execute(__import__('sqlalchemy').text("DELETE FROM rainfall"))
    conn.execute(__import__('sqlalchemy').text("DELETE FROM river_gauge"))
    conn.commit()

rain_all = []
gauge_all = []

# Process first 3 files
for i, f in enumerate(files[:3], 1):
    date = loaddata.parse_date(f)
    session = loaddata.get_session(f)
    if not date:
        print(f'  Skipping {loaddata.os.path.basename(f)} - no date found')
        continue

    print(f'  [{i}/3] Processing: {loaddata.os.path.basename(f)}')
    print(f'      Date: {date}, Session: {session}')

    rain_records = loaddata.extract_rainfall(f, date, session)
    gauge_records = loaddata.extract_gauge(f, date, session)

    rain_all.extend(rain_records)
    gauge_all.extend(gauge_records)

    print(f'      Rainfall: {len(rain_records)}, Gauge: {len(gauge_records)}')

# Save to database
print(f'\nSaving {len(rain_all)} rainfall and {len(gauge_all)} gauge records...')
if rain_all:
    df_rain = pd.DataFrame(rain_all)
    df_rain.to_sql("rainfall", engine, if_exists="append", index=False)
    print('  ✅ Rainfall data saved')

if gauge_all:
    df_gauge = pd.DataFrame(gauge_all)
    df_gauge.to_sql("river_gauge", engine, if_exists="append", index=False)
    print('  ✅ River gauge data saved')

print('\n✅ Test loading complete!')