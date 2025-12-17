from utils.db_connector import SnowflakeConnector

db = SnowflakeConnector()

queries = [
    "ALTER TABLE CANDIDATES ADD COLUMN IF NOT EXISTS SCREENING_SCORE FLOAT;"
]

print("Starting Schema Migration (Screening Score)...")
for q in queries:
    try:
        db.execute_transaction(q)
        print(f"Executed: {q}")
    except Exception as e:
        print(f"Error executing {q}: {e}")

print("Migration Completed.")
