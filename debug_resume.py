import sys
import os

# Add 'app' to path so we can import utils
sys.path.append(os.path.join(os.getcwd(), 'app'))

from utils.db_connector import SnowflakeConnector

def main():
    print("Checking Candidate Resume Data...")
    try:
        db = SnowflakeConnector()
        # Fetch ID, Name, and length of resume data for recent candidates
        query = "SELECT CANDIDATE_ID, NAME, LENGTH(RESUME_DATA) as RES_LEN, RESUME_URL FROM CANDIDATES ORDER BY ASSESSMENT_END_TIME DESC LIMIT 5"
        # Note: ASSESSMENT_END_TIME might be null if just applied. 
        # Using a safer order or just all.
        query = "SELECT NAME, RESUME_URL, RESUME_DATA FROM CANDIDATES"
        
        df = db.fetch_data(query)
        if not df.empty:
            for index, row in df.iterrows():
                data = row['RESUME_DATA']
                data_len = len(data) if data is not None else 0
                print(f"Candidate: {row['NAME']} | PDF: {row['RESUME_URL']} | Bytes: {data_len}")
        else:
            print("No candidates found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
