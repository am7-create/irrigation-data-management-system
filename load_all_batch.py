import loaddata
import pandas as pd
import os

# Load files in batches of 50
DATA_FOLDER = loaddata.DATA_FOLDER
files = loaddata.glob.glob(os.path.join(DATA_FOLDER, '**', '*.xlsx'), recursive=True)
files = [f for f in files if not os.path.basename(f).startswith('~$')]

print(f'Found {len(files)} Excel files')
print('Loading in batches of 50...')

loaddata.create_database()
engine = loaddata.get_engine()
loaddata.create_tables(engine)

# Clear existing data
with engine.connect() as conn:
    conn.execute(__import__('sqlalchemy').text('DELETE FROM rainfall'))
    conn.execute(__import__('sqlalchemy').text('DELETE FROM river_gauge'))
    conn.commit()

total_rain = 0
total_gauge = 0
batch_size = 50

for batch_start in range(0, len(files), batch_size):
    batch_end = min(batch_start + batch_size, len(files))
    batch_files = files[batch_start:batch_end]

    print(f'\n[Batch {batch_start//batch_size + 1}] Processing files {batch_start+1}-{batch_end}')

    rain_all = []
    gauge_all = []

    for f in batch_files:
        date = loaddata.parse_date(f)
        session = loaddata.get_session(f)
        if not date: continue

        rain_records = loaddata.extract_rainfall(f, date, session)
        gauge_records = loaddata.extract_gauge(f, date, session)

        rain_all.extend(rain_records)
        gauge_all.extend(gauge_records)

    # Save batch to database
    if rain_all:
        df_rain = pd.DataFrame(rain_all)
        df_rain.to_sql('rainfall', engine, if_exists='append', index=False)
    if gauge_all:
        df_gauge = pd.DataFrame(gauge_all)
        df_gauge.to_sql('river_gauge', engine, if_exists='append', index=False)

    total_rain += len(rain_all)
    total_gauge += len(gauge_all)

    print(f'  [+] Saved {len(rain_all)} rainfall, {len(gauge_all)} gauge records')
    print(f'  [Running total] {total_rain} rainfall, {total_gauge} gauge')

print(f'\n🎉 All data loaded successfully!')
print(f'📊 Final totals: {total_rain} rainfall records, {total_gauge} gauge records')
print(f'📁 Database: {loaddata.SQLITE_DB_PATH}')