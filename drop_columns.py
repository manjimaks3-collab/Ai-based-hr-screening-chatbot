from app.utils.db_connector import SnowflakeConnector

def migrate():
    print("Starting migration...")
    db = SnowflakeConnector()
    try:
        # Drop CITY
        print("Dropping CITY column...")
        try:
            db.execute_transaction("ALTER TABLE CANDIDATES DROP COLUMN CITY")
            print("CITY column dropped.")
        except Exception as e:
            if "does not exist" in str(e):
                print("CITY column does not exist or already dropped.")
            else:
                print(f"Error dropping CITY: {e}")

        # Drop STATE
        print("Dropping STATE column...")
        try:
            db.execute_transaction("ALTER TABLE CANDIDATES DROP COLUMN STATE")
            print("STATE column dropped.")
        except Exception as e:
            if "does not exist" in str(e):
                print("STATE column does not exist or already dropped.")
            else:
                print(f"Error dropping STATE: {e}")
                
        print("Migration complete.")
    except Exception as general_e:
        print(f"Migration failed: {general_e}")

if __name__ == "__main__":
    migrate()
