import loaddata
import pandas as pd

# Load first 10 files only
DATA_FOLDER = loaddata.DATA_FOLDER
files = loaddata.glob.glob(loaddata.os.path.join(DATA_FOLDER, '**', '*.xlsx'), recursive=True)
files = [f for f in files if not loaddata.os.path.basename(f).startswith('~$')]

print(f'Loading first 10 of {len(files)} files...')

loaddata.create_database()
engine = loaddata.get_engine()
loaddata.create_tables(engine)

# Clear existing data
with engine.connect() as conn:
    conn.execute(__import__('sqlalchemy').text('DELETE FROM rainfall'))
    conn.execute(__import__('sqlalchemy').text('DELETE FROM river_gauge'))
    conn.commit()

rain_all = []
gauge_all = []

for i, f in enumerate(files[:10], 1):
    date = loaddata.parse_date(f)
    session = loaddata.get_session(f)
    if not date: continue

    print(f'[{i:2d}/10] {loaddata.os.path.basename(f)}')
    rain_records = loaddata.extract_rainfall(f, date, session)
    gauge_records = loaddata.extract_gauge(f, date, session)

    rain_all.extend(rain_records)
    gauge_all.extend(gauge_records)

print(f'\nExtracted {len(rain_all)} rainfall and {len(gauge_all)} gauge records')

# Save to database
if rain_all:
    df_rain = pd.DataFrame(rain_all)
    df_rain.to_sql('rainfall', engine, if_exists='append', index=False)
if gauge_all:
    df_gauge = pd.DataFrame(gauge_all)
    df_gauge.to_sql('river_gauge', engine, if_exists='append', index=False)

print('✅ Data saved to database!')