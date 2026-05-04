import loaddata
import glob
import os

print('Testing data loader...')
print(f'Data folder: {loaddata.DATA_FOLDER}')
print(f'Folder exists: {os.path.exists(loaddata.DATA_FOLDER)}')

files = glob.glob(os.path.join(loaddata.DATA_FOLDER, '**', '*.xlsx'), recursive=True)
files = [f for f in files if not os.path.basename(f).startswith('~$')]
print(f'Found {len(files)} Excel files')

if files:
    print('First 10 files:')
    for f in files[:10]:
        date = loaddata.parse_date(f)
        session = loaddata.get_session(f)
        print(f'  {os.path.basename(f)} -> Date: {date}, Session: {session}')
        
    # Check files from different directories
    print('\nChecking files from different sessions:')
    morning_files = [f for f in files if 'morning' in f.lower()]
    evening_files = [f for f in files if 'evening' in f.lower()]
    
    if morning_files:
        f = morning_files[0]
        date = loaddata.parse_date(f)
        session = loaddata.get_session(f)
        print(f'  Morning: {os.path.basename(f)} -> Date: {date}, Session: {session}')
    
    if evening_files:
        f = evening_files[0]
        date = loaddata.parse_date(f)
        session = loaddata.get_session(f)
        print(f'  Evening: {os.path.basename(f)} -> Date: {date}, Session: {session}')
else:
    print('No Excel files found!')