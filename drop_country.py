from app.utils.db_connector import SnowflakeConnector

def migrate():
    print("Starting migration (Drop COUNTRY)...")
    db = SnowflakeConnector()
    try:
        # Drop COUNTRY
        print("Dropping COUNTRY column...")
        try:
            db.execute_transaction("ALTER TABLE CANDIDATES DROP COLUMN COUNTRY")
            print("COUNTRY column dropped.")
        except Exception as e:
            if "does not exist" in str(e):
                print("COUNTRY column does not exist or already dropped.")
            else:
                print(f"Error dropping COUNTRY: {e}")
                
        print("Migration complete.")
    except Exception as general_e:
        print(f"Migration failed: {general_e}")

if __name__ == "__main__":
    migrate()
