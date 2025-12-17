from utils.db_connector import SnowflakeConnector
import os

def init_db():
    print("Initializing Database...")
    db = SnowflakeConnector()
    
    # Read Schema File
    schema_path = os.path.join(os.path.dirname(__file__), '../sql/schema.sql')
    with open(schema_path, 'r') as f:
        sql_script = f.read()
        
    # Split into statements
    statements = sql_script.split(';')
    
    conn = db.get_connection()
    if not conn:
        print("Failed to connect to Snowflake. Check .env variables.")
        return

    try:
        cur = conn.cursor()
        for stmt in statements:
            # Split statement into lines and remove comment-only lines
            lines = stmt.split('\n')
            valid_lines = [line for line in lines if line.strip() and not line.strip().startswith('--')]
            stmt_clean = '\n'.join(valid_lines).strip()
            
            if not stmt_clean:
                continue
                
            print(f"Executing: {stmt_clean[:50]}...")
            cur.execute(stmt_clean)
        print("Database initialized successfully!")
        
        # Create Default Admin
        print("Creating default admin (admin/admin123)...")
        db.create_admin("admin", "admin123")
        print("Default admin created.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
