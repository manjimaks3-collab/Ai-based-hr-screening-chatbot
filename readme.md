# HR Screening System - Reconstruction Blueprint

This document acts as a complete blueprint to reconstruct the **HR Screening System** from scratch. It contains the architecture, database schema, and logic flow required to build the application without prior context.

## 1. System Overview
**Goal**: Automate the recruitment process including Resume Parsing, Technical Assessment, and AI Chat Screening.
**Tech Stack**:
*   **Language**: Python 3.8+
*   **Frontend**: Streamlit
*   **Database**: Snowflake
*   **AI**: Google Gemini Pro (Generative AI)
*   **Email**: SMTP (Gmail)
*   **Key Libraries**: `snowflake-connector-python`, `pandas`, `scikit-learn`, `PyPDF2`, `google-generativeai`.

---

## 2. Database Schema (Snowflake)
To replicate the database, run the following SQL queries in your Snowflake Worksheet.

### Table: JOBS
Stores metadata for job postings.
```sql
CREATE OR REPLACE TABLE JOBS (
    JOB_ID STRING PRIMARY KEY,
    TITLE STRING,
    DESCRIPTION STRING,
    REQUIRED_SKILLS STRING,
    ASSESSMENT_QUESTIONS VARIANT, -- JSON Array: [{"id":1, "text":"...", "options":["A","B"], "answer":"A"}]
    MIN_ATS_SCORE INT DEFAULT 50, -- Minimum percentage to pass resume check
    TIME_LIMIT_MINUTES INT DEFAULT 30, -- Timer for assessment
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### Table: ADMINS
Stores credentials for HR access.
```sql
CREATE OR REPLACE TABLE ADMINS (
    USERNAME STRING PRIMARY KEY,
    PASSWORD STRING, -- Plain text for demo, Hash for prod
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
-- Insert initial admin:
INSERT INTO ADMINS (USERNAME, PASSWORD) VALUES ('admin', 'admin123');
```

### Table: CANDIDATES
Stores application data, file blobs, and scores.
```sql
CREATE OR REPLACE TABLE CANDIDATES (
    CANDIDATE_ID STRING PRIMARY KEY,
    JOB_ID STRING,
    NAME STRING,
    EMAIL STRING,
    PHONE STRING,
    CITY STRING,
    STATE STRING,
    COUNTRY STRING,
    WORK_EXPERIENCE STRING,
    EDUCATION_LEVEL STRING,
    RESUME_URL STRING,          -- Original filename
    RESUME_DATA BINARY,         -- PDF File Content (BLOB)
    ATS_SCORE FLOAT,            -- 0-100 score based on resume match
    ATS_PASS BOOLEAN,
    ASSESSMENT_SCORE FLOAT,     -- 0-100 score from MCQ
    ASSESSMENT_START_TIME TIMESTAMP_NTZ,
    ASSESSMENT_END_TIME TIMESTAMP_NTZ,
    CHAT_TRANSCRIPT VARIANT,    -- JSON list of chat messages
    SCREENING_SCORE FLOAT,      -- 0-100 score from AI Chat analysis
    APPLICATION_DETAILS VARIANT, -- JSON of extra details
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (JOB_ID) REFERENCES JOBS(JOB_ID)
);
```

---

## 3. Environment Configuration
Create a `.env` file in the root directory.

```ini
# --- Database (Snowflake) ---
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account_id
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HR_DB
SNOWFLAKE_SCHEMA=PUBLIC

# --- Email (SMTP) ---
# Note: For Gmail, use an App Password (requires 2FA enabled on Google Account)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_google_app_password

# --- AI (Google Gemini) ---
GOOGLE_API_KEY=your_gemini_api_key
```

---

## 4. Application Logic & Modules

### `app/Home.py` (Entry Point)
*   **Logic**: Handles Login. **Auto-Initializes Database** on startup (creats tables if missing).
*   **Tabs**:
    1.  **Candidate Login**: Checks `CANDIDATES` table (Email/Phone). Redirects to `Candidate_Application`.
    2.  **Register**: New Candidates sign up here (Insert into `CANDIDATES`).
    3.  **Admin Login**: Checks `ADMINS` table. Redirects to `Admin_Dashboard`.

### `app/pages/1_Candidate_Application.py` (Core Flow)
*   **Step 1 (Resume)**: Upload PDF -> Extract Text (`PyPDF2`) -> Calculate ATS Score (Cosine Similarity vs Job Desc) -> Save PDF Blob to DB (Binary).
*   **Step 2 (MCQ)**: If ATS Pass -> Show Questions (fetched from `JOBS`). Display JS Countdown Timer based on `TIME_LIMIT_MINUTES`.
*   **Step 3 (Chat)**: Interactive Chatbot. At end -> Send history to Google Gemini API (`utils/ai_screener`) -> Update `SCREENING_SCORE`.

### `app/pages/2_Admin_Dashboard.py`
*   **Tab 1 (Post Job)**: Form to add Title, Skills. "Add Question" section to build JSON for `ASSESSMENT_QUESTIONS`. Inputs for `MIN_ATS_SCORE` and `TIME_LIMIT`.
*   **Tab 2 (Edit Job)**: Select existing job -> Load data -> Update/Delete.
*   **Tab 3 (Leaderboard)**: List Candidates (Excludes Profile-only records). Sorted by Assessment Score > ATS Score. Dropdown to **Download Resume** (fetches `RESUME_DATA` blob from DB).
*   **Sidebar (Danger Zone)**:
    *   **Initialize Database**: Recreates missing tables (`JOBS`, `CANDIDATES`, `ADMINS`) and resets Default Admin (`admin`/`admin123`).
    *   **Clear All Data**: Truncates/Deletes all candidate and job records.

### `app/utils/`
*   `db_connector.py`: Handles all Snowflake SQL execution (`execution_transaction`, `fetch_data`).
*   `ai_screener.py`: Uses `google.generativeai` to score chat transcripts.
*   `ats_engine.py`: Logic for text cleaning and similarity scoring (`sklearn.metrics.pairwise.cosine_similarity`).

---

## 5. installation
1.  **Clone/Create Folder**: `hr-screening-system`
2.  **Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Run**:
    ```bash
   
    ```
 python -m streamlit run app/Home.py