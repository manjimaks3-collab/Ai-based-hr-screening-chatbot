from utils.db_connector import SnowflakeConnector
import pandas as pd

db = SnowflakeConnector()
email = "milimariya2004@gmail.com"

# Fetch candidate by email
query = "SELECT * FROM CANDIDATES WHERE EMAIL = %s ORDER BY CREATED_AT DESC LIMIT 1"
df = db.fetch_data(query, (email,))

if not df.empty:
    row = df.iloc[0]
    print(f"Candidate: {row['NAME']}")
    print(f"ID: {row['CANDIDATE_ID']}")
    print(f"ATS_PASS: {row['ATS_PASS']}")
    print(f"ASSESSMENT_SCORE: {row['ASSESSMENT_SCORE']}")
    print(f"Type of Score: {type(row['ASSESSMENT_SCORE'])}")
    print(f"CHAT_TRANSCRIPT: {row['CHAT_TRANSCRIPT'] is not None}")
else:
    print("No candidate found.")
