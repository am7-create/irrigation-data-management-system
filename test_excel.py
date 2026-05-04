import loaddata
import pandas as pd

# Test with just one file
DATA_FOLDER = loaddata.DATA_FOLDER
files = loaddata.glob.glob(loaddata.os.path.join(DATA_FOLDER, '**', '*.xlsx'), recursive=True)
files = [f for f in files if not loaddata.os.path.basename(f).startswith('~$')]

if files:
    test_file = files[0]
    print(f'Testing with file: {loaddata.os.path.basename(test_file)}')

    date = loaddata.parse_date(test_file)
    session = loaddata.get_session(test_file)
    print(f'Date: {date}, Session: {session}')

    try:
        rain_records = loaddata.extract_rainfall(test_file, date, session)
        gauge_records = loaddata.extract_gauge(test_file, date, session)

        print(f'Rainfall records extracted: {len(rain_records)}')
        print(f'River gauge records extracted: {len(gauge_records)}')

        if rain_records:
            print('Sample rainfall record:')
            print(rain_records[0])

        if gauge_records:
            print('Sample gauge record:')
            print(gauge_records[0])

    except Exception as e:
        print(f'Error extracting data: {e}')
        import traceback
        traceback.print_exc()
else:
    print('No files found')