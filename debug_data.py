import loaddata
import glob
import os

print('Testing data folder access...')
files = glob.glob(os.path.join(loaddata.DATA_FOLDER, '**', '*.xlsx'), recursive=True)
files = [f for f in files if not os.path.basename(f).startswith('~$')]
print(f'Found {len(files)} Excel files')
for f in files[:5]:  # Show first 5 files
    print(f'  {os.path.basename(f)}')

print(f'Data folder: {loaddata.DATA_FOLDER}')
print(f'Folder exists: {os.path.exists(loaddata.DATA_FOLDER)}')