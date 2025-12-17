from utils.db_connector import SnowflakeConnector

db = SnowflakeConnector()

queries = [
    # Add RESUME_DATA binary file column
    "ALTER TABLE CANDIDATES ADD COLUMN IF NOT EXISTS RESUME_DATA BINARY;"
]

print("Starting Schema Migration (Resume Blob)...")
for q in queries:
    try:
        db.execute_transaction(q)
        print(f"Executed: {q}")
    except Exception as e:
        print(f"Error executing {q}: {e}")

print("Migration Completed.")
