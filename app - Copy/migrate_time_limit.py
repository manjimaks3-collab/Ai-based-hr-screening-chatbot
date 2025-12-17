from utils.db_connector import SnowflakeConnector

db = SnowflakeConnector()

queries = [
    # Add TIME_LIMIT_MINUTES to JOBS table
    "ALTER TABLE JOBS ADD COLUMN IF NOT EXISTS TIME_LIMIT_MINUTES INT DEFAULT 30;"
]

print("Starting Schema Migration (Time Limit)...")
for q in queries:
    try:
        db.execute_transaction(q)
        print(f"Executed: {q}")
    except Exception as e:
        print(f"Error executing {q}: {e}")

print("Migration Completed.")
