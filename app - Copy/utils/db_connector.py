import snowflake.connector
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class SnowflakeConnector:
    def __init__(self):
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = os.getenv("SNOWFLAKE_DATABASE")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA")

    def get_connection(self):
        try:
            conn = snowflake.connector.connect(
                user=self.user,
                password=self.password,
                account=self.account,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema
            )
            return conn
        except Exception as e:
            # Raise exception so calling functions know it failed
            raise Exception(f"Snowflake Connection Failed: {str(e)}")

    def run_query(self, query, params=None):
        # Kept for backward compatibility or raw cursor access if needed
        conn = self.get_connection() # Will raise if fails
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur
        except Exception as e:
            raise Exception(f"Query Execution Failed: {str(e)}")
        # Note: Connection is not closed here. relying on GC or caller.

    def execute_transaction(self, query, params=None):
        """Executes a DML query (INSERT/UPDATE/DELETE) with commit."""
        conn = self.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Transaction Failed: {str(e)}")
        finally:
            conn.close()

    def fetch_data(self, query, params=None):
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute(query, params)
            df = cur.fetch_pandas_all()
            conn.close()
            return df
        except Exception as e:
            print(f"Fetch Logic Error: {e}")
            # Returing empty DF is safer for UI rendering than crashing
            return pd.DataFrame()

    def insert_candidate(self, candidate_data):
        query = """
        INSERT INTO CANDIDATES 
        (CANDIDATE_ID, JOB_ID, NAME, EMAIL, PHONE, WORK_EXPERIENCE, 
         EDUCATION_LEVEL, RESUME_URL, ATS_SCORE, ATS_PASS, APPLICATION_DETAILS, RESUME_DATA)
        SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, parse_json(%s), TO_BINARY(%s)
        """
        params = (
            candidate_data['id'], candidate_data['job_id'], candidate_data['name'], 
            candidate_data['email'], candidate_data['phone'],
            candidate_data['experience'],
            candidate_data['education'], candidate_data['resume_url'], candidate_data['ats_score'],
            candidate_data['ats_pass'], candidate_data['details_json'],
            candidate_data.get('resume_blob') # New Binary
        )
        self.execute_transaction(query, params)

    def insert_job(self, job_data):
        query = """
        INSERT INTO JOBS (JOB_ID, TITLE, DESCRIPTION, REQUIRED_SKILLS, ASSESSMENT_QUESTIONS, MIN_ATS_SCORE, TIME_LIMIT_MINUTES)
        SELECT %s, %s, %s, %s, parse_json(%s), %s, %s
        """
        params = (
            job_data['id'], 
            job_data['title'], 
            job_data['description'], 
            job_data['skills'], 
            job_data.get('questions_json', '[]'),
            job_data.get('min_ats_score', 50),
            job_data.get('time_limit', 30)
        )
        self.execute_transaction(query, params)

    def fetch_all_candidates(self):
        # Sort by Assessment Score (High to Low), then ATS Score (High to Low)
        # Exclude heavy RESUME_DATA column for list view
        # Exclude 'PROFILE' records (registration only)
        query = "SELECT * EXCLUDE (RESUME_DATA) FROM CANDIDATES WHERE JOB_ID != 'PROFILE' ORDER BY FINAL_SCORE DESC NULLS LAST, ASSESSMENT_SCORE DESC NULLS LAST"
        return self.fetch_data(query)

    def get_candidate_resume(self, candidate_id):
        # Fetch just the blob
        query = "SELECT RESUME_URL, RESUME_DATA FROM CANDIDATES WHERE CANDIDATE_ID = %s"
        df = self.fetch_data(query, (candidate_id,))
        return df.iloc[0] if not df.empty else None

    def fetch_jobs(self):
        query = "SELECT * FROM JOBS"
        return self.fetch_data(query)
        
    def get_job_details(self, job_id):
        query = "SELECT * FROM JOBS WHERE JOB_ID = %s"
        df = self.fetch_data(query, (job_id,))
        return df.iloc[0] if not df.empty else None

    def update_chat_transcript(self, candidate_id, transcript_json, screening_score):
        query = "UPDATE CANDIDATES SET CHAT_TRANSCRIPT = parse_json(%s), SCREENING_SCORE = %s WHERE CANDIDATE_ID = %s"
        params = (transcript_json, screening_score, candidate_id)
        self.execute_transaction(query, params)


    def update_job(self, job_data):
        query = """
        UPDATE JOBS 
        SET TITLE=%s, DESCRIPTION=%s, REQUIRED_SKILLS=%s, ASSESSMENT_QUESTIONS=parse_json(%s), 
            MIN_ATS_SCORE=%s, TIME_LIMIT_MINUTES=%s
        WHERE JOB_ID=%s
        """
        params = (
            job_data['title'], job_data['description'], job_data['skills'],
            job_data.get('questions_json', '[]'),
            job_data.get('min_ats_score', 50),
            job_data.get('time_limit', 30),
            job_data['id']
        )
        self.execute_transaction(query, params)
        
    def delete_job(self, job_id):
        query = "DELETE FROM JOBS WHERE JOB_ID = %s"
        self.execute_transaction(query, (job_id,))

    def update_candidate_assessment(self, candidate_id, score):
        query = "UPDATE CANDIDATES SET ASSESSMENT_SCORE = %s WHERE CANDIDATE_ID = %s"
        params = (score, candidate_id)
        self.execute_transaction(query, params)

    def update_final_score(self, candidate_id, final_score):
        query = "UPDATE CANDIDATES SET FINAL_SCORE = %s WHERE CANDIDATE_ID = %s"
        params = (final_score, candidate_id)
        self.execute_transaction(query, params)

    def authenticate_admin(self, username, password):
        query = "SELECT USERNAME FROM ADMINS WHERE USERNAME = %s AND PASSWORD = %s"
        df = self.fetch_data(query, (username, password))
        return not df.empty

    def authenticate_candidate(self, email, phone):
        query = "SELECT * FROM CANDIDATES WHERE EMAIL = %s AND PHONE = %s"
        df = self.fetch_data(query, (email, phone))
        return df.iloc[0] if not df.empty else None

    def get_application_status(self, email, job_id):
        # Find existing application for this job (excluding the profile record if needed, but here searching by job_id is enough)
        query = "SELECT * FROM CANDIDATES WHERE EMAIL = %s AND JOB_ID = %s"
        df = self.fetch_data(query, (email, job_id))
        return df.iloc[0] if not df.empty else None

    def get_candidate_by_id(self, candidate_id):
        query = "SELECT * FROM CANDIDATES WHERE CANDIDATE_ID = %s"
        df = self.fetch_data(query, (candidate_id,))
        return df.iloc[0] if not df.empty else None

    def update_candidate_assessment(self, candidate_id, score, duration_seconds=0):
        query = "UPDATE CANDIDATES SET ASSESSMENT_SCORE = %s, ASSESSMENT_END_TIME = CURRENT_TIMESTAMP(), ASSESSMENT_DURATION_SECONDS = %s WHERE CANDIDATE_ID = %s"
        params = (score, duration_seconds, candidate_id)
        self.execute_transaction(query, params)

    def create_admin(self, username, password):
        # Helper for setup
        query = "MERGE INTO ADMINS AS target USING (SELECT %s AS U, %s AS P) AS source ON target.USERNAME = source.U WHEN MATCHED THEN UPDATE SET PASSWORD = source.P WHEN NOT MATCHED THEN INSERT (USERNAME, PASSWORD) VALUES (source.U, source.P)"
        self.execute_transaction(query, (username, password))





    def register_candidate(self, name, email, phone):
        # Check if already exists to avoid duplicates
        if self.authenticate_candidate(email, phone) is not None:
             return False # Already exists

        query = """
        INSERT INTO CANDIDATES (CANDIDATE_ID, JOB_ID, NAME, EMAIL, PHONE)
        VALUES (%s, 'PROFILE', %s, %s, %s)
        """
        import uuid
        c_id = str(uuid.uuid4())
        params = (c_id, name, email, phone)
        self.execute_transaction(query, params)
        return True
    def update_job(self, job_data):
        query = """
        UPDATE JOBS 
        SET TITLE = %s, DESCRIPTION = %s, REQUIRED_SKILLS = %s, ASSESSMENT_QUESTIONS = parse_json(%s)
        WHERE JOB_ID = %s
        """
        params = (
            job_data['title'],
            job_data['description'],
            job_data['skills'],
            job_data.get('questions_json', '[]'),
            job_data['id']
        )
        self.execute_transaction(query, params)

    def delete_job(self, job_id):
        query = "DELETE FROM JOBS WHERE JOB_ID = %s"
        self.execute_transaction(query, (job_id,))

    def clear_all_data(self):
        """
        Deletes all data from CANDIDATES and JOBS tables.
        This is a destructive action.
        """
        # Using DELETE FROM instead of TRUNCATE for broader compatibility if permissions vary, 
        # but TRUNCATE is cleaner. Let's try TRUNCATE first, fallback/separate calls?
        # Creating a stored procedure or just two calls.
        
        # Transaction 1: Candidates
        self.execute_transaction("DELETE FROM CANDIDATES")
        # Transaction 2: Jobs 
        self.execute_transaction("DELETE FROM JOBS")

    def init_db(self):
        """
        Creates necessary tables if they do not exist.
        """
        # 1. JOBS Table
        q_jobs = """
        CREATE TABLE IF NOT EXISTS JOBS (
            JOB_ID VARCHAR(255) PRIMARY KEY,
            TITLE VARCHAR(255),
            DESCRIPTION TEXT,
            REQUIRED_SKILLS TEXT,
            ASSESSMENT_QUESTIONS VARIANT,
            MIN_ATS_SCORE INT DEFAULT 50,
            TIME_LIMIT_MINUTES INT DEFAULT 30
        )
        """
        self.execute_transaction(q_jobs)

        # 2. CANDIDATES Table
        q_candidates = """
        CREATE TABLE IF NOT EXISTS CANDIDATES (
            CANDIDATE_ID VARCHAR(255) PRIMARY KEY,
            JOB_ID VARCHAR(255),
            NAME VARCHAR(255),
            EMAIL VARCHAR(255),
            PHONE VARCHAR(50),
            WORK_EXPERIENCE VARCHAR(50), 
            EDUCATION_LEVEL VARCHAR(100),
            RESUME_URL VARCHAR(500),
            ATS_SCORE FLOAT,
            ATS_PASS BOOLEAN,
            APPLICATION_DETAILS VARIANT,
            RESUME_DATA BINARY,
            CHAT_TRANSCRIPT VARIANT,
            SCREENING_SCORE FLOAT,
            ASSESSMENT_SCORE FLOAT,
            ASSESSMENT_END_TIME TIMESTAMP,
            ASSESSMENT_DURATION_SECONDS INT,
            APPLICATION_SCORE FLOAT,
            FINAL_SCORE FLOAT
        )
        """
        self.execute_transaction(q_candidates)

        # 3. ADMINS Table
        q_admins = """
        CREATE TABLE IF NOT EXISTS ADMINS (
            USERNAME VARCHAR(255) PRIMARY KEY,
            PASSWORD VARCHAR(255)
        )
        """
        self.execute_transaction(q_admins)

        # 4. Default Admin User
        # Using MERGE to ensure it exists without duplicates
        q_default_admin = """
        MERGE INTO ADMINS AS target 
        USING (SELECT 'admin' AS U, 'admin123' AS P) AS source 
        ON target.USERNAME = source.U 
        WHEN MATCHED THEN UPDATE SET PASSWORD = source.P 
        WHEN NOT MATCHED THEN INSERT (USERNAME, PASSWORD) VALUES (source.U, source.P)
        """
        self.execute_transaction(q_default_admin)



