from utils.db_connector import SnowflakeConnector

db = SnowflakeConnector()

queries = [
    # Add MIN_ATS_SCORE to JOBS table if it doesn't exist
    "ALTER TABLE JOBS ADD COLUMN IF NOT EXISTS MIN_ATS_SCORE FLOAT DEFAULT 50;"
]

print("Starting Schema Migration...")
for q in queries:
    try:
        db.execute_transaction(q)
        print(f"Executed: {q}")
    except Exception as e:
        print(f"Error executing {q}: {e}")

print("Migration Completed.")
