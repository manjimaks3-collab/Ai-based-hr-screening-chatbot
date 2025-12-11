# Resume-screening-for-HR-round

The HR Interview Screening Chatbot is a cloud-based intelligent system that automates the initial stages of recruitment.  
It simulates a real-world hiring workflow used by companies:

“Resume → Application → ATS Filter → Assessment Link → Assessment Scoring → HR Shortlist”

The system uses Streamlit + Python for the applicant interface, Snowflake as the data warehouse, Azure for deployment and email automation, and Power BI for recruiter dashboards.

The goal of the project is to reduce recruiter workload and shortlist the most relevant candidates using a transparent and explainable AI scoring system.

---

## Key Features

### 1. Candidate Application Portal (Streamlit)
- Candidate fills an application form.  
- Uploads PDF resume.  
- Stores submission in Snowflake.  
- Shows message: “Assessment link will be emailed if your resume passes ATS filter.”

### 2. ATS Resume Filtering (Python + NLP)
- Keywords and skill extraction.  
- Semantic similarity scoring.  
- Computes ATS Score (0–100).  
- If ATS score ≥ threshold, an assessment link is emailed.

### 3. Assessment Workflow
- Candidate receives secure link via email.  
- Takes the MCQ/coding assessment.  
- System auto-grades and stores the result.  
- Assessment score is compared with the threshold.

### 4. Final Composite Scoring
For candidates who pass both gates, the system evaluates:
- Resume Score  
- Application Form Answer Score  
- Assessment Score  

All three are combined to calculate a composite AI score.

### 5. Recruiter Dashboard (Power BI)
- Displays top candidates.  
- Filters by ATS, Assessment, and Final Score.  
- View resume information and summaries.  
- Provides transparent score breakdowns.

---

## Why This Project Is Useful

Recruiters handle thousands of applications. Manually checking resumes, distributing assessments, scoring results, and shortlisting candidates is slow.

This system automates:
- Resume screening  
- Assessment distribution  
- Scoring  
- Shortlisting  
- Candidate ranking  

It improves fairness, consistency, and reduces workload by 70–80%.

---

## Process Flow

### 1. Candidate Submission
Candidates visit the Streamlit app and:
- Fill personal details  
- Upload resume (PDF only)  
- Answer basic application questions  

Data is stored in Snowflake.

### 2. ATS Scoring
ATS score is calculated using:
- Extracted skills  
- Keywords  
- Role requirements  
- Semantic similarity  

If ATS Score ≥ ATS_MIN, the candidate moves forward.  
If not, the application ends.

### 3. Assessment Link Generation
If ATS passes:
- The system generates a secure assessment token  
- Sends the assessment link to the candidate’s email  

### 4. Candidate Completes Assessment
Candidate takes the assessment, which may include:
- MCQs  
- Optional coding tasks  

Python backend auto-grades the submission, and the score is stored.

### 5. Assessment Gate
If Assessment Score ≥ ASSESSMENT_MIN, the candidate proceeds to HR evaluation.  
Otherwise, the candidate is rejected.

### 6. Composite AI Scoring
For candidates who pass both gates:

final_score = 0.4 * resume_score + 0.3 * application_score + 0.3 * assessment_score

A detailed score breakdown is stored for transparency.

### 7. Recruiter Shortlist
The Power BI dashboard shows:
- Final Score  
- ATS Score  
- Assessment Score  
- Resume keywords  
- Application answers  

Recruiters review only the shortlisted profiles.

---

## System Architecture

           +-----------------------------+
           |       Streamlit UI          |
           | (Resume + Application Form) |
           +-------------+---------------+
                         |
                         v
           +-----------------------------+
           |      Python Backend         |
           |  ATS Scoring + NLP Parsing  |
           +-------------+---------------+
                         |
                         v
           +-----------------------------+
           |          Snowflake          |
           |  (Candidate & Score Data)   |
           +-------------+---------------+
                         |
                         v
           +-----------------------------+
           |     Assessment Service      |
           | (MCQ/Coding Auto-Grading)   |
           +-------------+---------------+
                         |
                         v
           +-----------------------------+
           |   Composite Scoring Engine  |
           +-------------+---------------+
                         |
                         v
           +-----------------------------+
           |      Power BI Dashboard     |
           |     (HR Shortlist View)     |
           +-----------------------------+


### Cloud Components (Azure)
- Azure App Service / Container Apps: Deploy Streamlit and backend  
- Azure Blob Storage: Store resumes (PDF)  
- Azure Key Vault: Store Snowflake credentials  
- Azure Function / SendGrid: Email assessment link  

---

## Tech Stack

Frontend: Streamlit  
Backend: Python (NLP for ATS scoring)  
Database / DW: Snowflake  
Cloud: Azure (App Service, Blob Storage, Key Vault, Azure Function for email sending)  
Visualization: Power BI  



