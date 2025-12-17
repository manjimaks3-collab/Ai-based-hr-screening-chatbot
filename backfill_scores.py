from app.utils.db_connector import SnowflakeConnector
import pandas as pd

def backfill():
    print("Starting backfill...")
    db = SnowflakeConnector()
    try:
        # Fetch all candidates
        df = db.fetch_all_candidates()
        print(f"Found {len(df)} candidates.")

        for index, row in df.iterrows():
            c_id = row['CANDIDATE_ID']
            final_score = row.get('FINAL_SCORE')
            
            # Check if Final Score is missing (NaN or None)
            if pd.isna(final_score):
                print(f"Updating Candidate {c_id}...")
                
                ats = row.get('ATS_SCORE') if not pd.isna(row.get('ATS_SCORE')) else 0
                ass = row.get('ASSESSMENT_SCORE') if not pd.isna(row.get('ASSESSMENT_SCORE')) else 0
                scr = row.get('SCREENING_SCORE') if not pd.isna(row.get('SCREENING_SCORE')) else 0
                
                # Assume if they haven't done it, it's 0. Or maybe we shouldn't calculate if they haven't finished?
                # User wants "Final Score", usually implies completion.
                # However, to fill "None", we'll calculate based on what we have.
                # If they haven't passed ATS, etc.
                
                new_final = (ats + ass + scr) / 3
                
                try:
                    db.update_final_score(c_id, new_final)
                    print(f" -> Set Final Score to {new_final:.2f}")
                except Exception as e:
                    print(f" -> Failed to update: {e}")
            else:
                # print(f"Candidate {c_id} already has score {final_score}")
                pass
                
        print("Backfill complete.")

    except Exception as e:
        print(f"Backfill Error: {e}")

if __name__ == "__main__":
    backfill()
