from utils.db_connector import SnowflakeConnector
import pandas as pd
import json

db = SnowflakeConnector()
df = db.fetch_jobs()

print(f"Total Jobs: {len(df)}")
for idx, row in df.iterrows():
    print(f"--- Job: {row['TITLE']} ({row['JOB_ID']}) ---")
    raw_qs = row['ASSESSMENT_QUESTIONS']
    print(f"Type: {type(raw_qs)}")
    print(f"Value: {raw_qs}")
    
    if raw_qs:
        try:
            # Check if it loads
            if isinstance(raw_qs, str):
                parsed = json.loads(raw_qs)
                print(f"Parsed Length: {len(parsed)}")
            else:
                print(f"Already parsed/Not a string. Length: {len(raw_qs) if hasattr(raw_qs, '__len__') else 'N/A'}")
        except Exception as e:
            print(f"JSON Parse Error: {e}")
    else:
        print("Empty/Null")
