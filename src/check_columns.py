import pandas as pd
import os
files = [
    'data/hanatour_reviews.csv',
    'data/processed_aviation_performance.csv',
    'data/hanatour_all_itineraries.csv',
    'data/hanatour_danang_integrated.csv',
    'data/hanatour_nhatrang_integrated.csv',
    'data/hanatour_singapore_integrated.csv'
]
for file in files:
    if os.path.exists(file):
        try:
            df = pd.read_csv(file, encoding='utf-8-sig', nrows=1)
            print(f"File: {file}")
            print(f"Columns: {list(df.columns)}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    else:
        print(f"File not found: {file}")