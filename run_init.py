import sys
import os

# Add 'app' to path so we can import utils
sys.path.append(os.path.join(os.getcwd(), 'app'))

from utils.db_connector import SnowflakeConnector

def main():
    print("Initializing Database...")
    try:
        db = SnowflakeConnector()
        db.init_db()
        print("Success! Database initialized and default admin (admin/admin123) created.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
