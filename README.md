# Resume-screening-for-HR-round

The HR Interview Screening Chatbot is a cloud-based intelligent system that automates the initial stages of recruitment.  
It simulates a real-world hiring workflow used by companies:

“Resume → Application → ATS Filter -> Mail"
---
"Mail→ Assessment Link → Assessment Scoring → HR Shortlist”
---
The system uses Streamlit + Python for the applicant interface, HTML and CSS and vanilla JS for assesment interface, Snowflake as the data warehouse, Azure for deployment and email automation, and Power BI for recruiter dashboards.

The goal of the project is to reduce recruiter workload and shortlist the most relevant candidates using a transparent and explainable AI scoring system.

---

## Key Features
### Admin page :
     Job decscription is available here, assesment questions depends on jd. key words are also in Jd.
     
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

### Admin page :
     Job decscription is available here, assesment questions depends on jd. key words are also in Jd.

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
           |     Assessment Service 
           |         HTML & CSS
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

Frontend: Streamlit, HTML, CSS
Backend: Python (NLP for ATS scoring)  
Database / DW: Snowflake  
Cloud: Azure (App Service, Blob Storage, Key Vault, Azure Function for email sending)  
Visualization: Power BI  

## Project Descriptiion
- Admin page has JD, After the candidate fills the application and the application questions consists of :(name, email, gender, ph no, city, state, country, pincode, address, applied role, work experience, languages known, highest level of education, name of university, feild of study, year of graduation, skills, resume url,CTC expected, why this company, do you have the work permit of the applied country, do you in future require any help from the company for visa permit) and then the application is submitted and the ats scoring takes place based on the keyword matching and if the ats score is equal or higher than what we set teh candidate will be get the assessment link through mail ----> python+streamlit--> stored in snowflake

-after the candidate receives the mail and starts the assignment and the assignment consists of 10 qestions(MCQ)(MCQ, options, answers all stored in seperate snowflake table) and the candidate submits the assessment and the assesment should be scored and if the assesment score is higher than the given score the candidate goes under holistic screening that consists of resume screening + assesment score + application answers(application answers means CTC, work permit eligibilty is taken as base ) and if the avarage score is equal or higher than the score set then the candidate is shortlisted to present on power bi for HR ----> HTML, CSS, Vanilla JS ---> stored in snowflake

-HR has a view of shortlisted candidates in table and graph of their selection reason(CTC, keyword matching kindaa)---> power bi

## Database details:
Name, email, gender, phno, city, state, pincode, country, address, applied role, resume url, ats score, ats pass, assesment token, assesment score, final score, key word score, shortlisted, shortlisted score, job description, skills, work experience, languages known, highest level of education, name of university, feild of study, year of graduation 


## Abstract :
Recruitment is one of the most critical and challenging functions in modern organizations, where early and accurate candidate screening plays a vital role in improving hiring quality and operational efficiency. Traditional recruitment processes, such as manual resume screening, written examinations, and preliminary interviews, are time-consuming, resource-intensive, and susceptible to human bias and inconsistency. With the increasing volume of job applications, there is a growing need for automated and intelligent screening mechanisms. Recent advancements in artificial intelligence (AI), automation, and data-driven systems have shown significant potential in transforming recruitment workflows by improving efficiency, consistency, and decision quality.

This study proposes an intelligent AI-based HR screening system that integrates automated resume screening, structured online assessments, and centralized candidate scoring to support effective recruitment decision-making. The system utilizes Applicant Tracking System (ATS)-based resume analysis to evaluate resume relevance against job requirements, followed by Python-based online assessments to measure candidates’ technical knowledge and aptitude. A composite scoring mechanism combines resume scores, application data, and assessment results to generate an objective shortlist of candidates. The application and job management functionalities are implemented using Streamlit, while Snowflake serves as the centralized data repository. Power BI is employed to visualize shortlisted candidates and performance metrics for HR decision-makers.

The proposed system was evaluated using sample candidate datasets to analyze its screening accuracy, consistency, and efficiency. Experimental results indicate that the automated screening framework significantly reduces manual effort, improves shortlisting accuracy, and ensures consistent evaluation compared to traditional recruitment methods. The centralized scoring and ranking mechanism enables recruiters to make faster and more informed hiring decisions.

This work contributes to AI-driven recruitment research by presenting a scalable, automated, and practical screening framework suitable for real-world hiring scenarios. The findings suggest that intelligent HR screening systems can enhance recruitment transparency, reduce administrative workload, and improve overall hiring effectiveness. Future enhancements may include the integration of explainable AI techniques, predictive analytics for hiring outcomes, and advanced interview analysis to further strengthen recruitment intelligence.


## Working:

WORKING OF THE SYSTEM

The proposed AI-based HR screening system automates the initial stages of recruitment by integrating application management, resume screening, assessment evaluation, and candidate shortlisting into a unified workflow. The system operates through the following sequential stages:


---

1. User Registration and Login

The system provides role-based authentication using a Streamlit interface. Users can register and log in as either Candidate or Admin.

Candidates can register, log in, view available job postings, and submit applications.

Admin users can log in to manage job postings and monitor candidate data.


This role-based access ensures secure and controlled interaction with the system.


---

2. Job Posting and Management (Admin)

After logging in, the Admin can:

Post new job openings with required skills and qualifications.

Edit or update existing job postings.

View candidate application data stored in the database.


All job-related information is stored in the Snowflake database and dynamically displayed to candidates through the Streamlit interface.


---

3. Application Submission (Candidate)

Candidates log in and apply for a selected job by:

Filling out the application form.

Uploading their resume in PDF format.


The submitted application and resume are validated and securely stored in Snowflake for further processing. At this stage, candidates can only submit applications and cannot view any screening scores.


---

4. ATS-Based Resume Screening

Once an application is submitted, the system automatically performs ATS-based resume screening using Python.

The resume is parsed to extract keywords and skills.

The extracted data is compared with job requirements.

An ATS score is generated for each candidate.


If the ATS score does not meet the predefined threshold, the candidate is rejected. If the threshold is met, the candidate proceeds to the next stage.


---

5. Online Assessment Evaluation

Candidates who pass the ATS screening are assigned an online assessment.

The assessment is generated and evaluated using Python.

The assessment tests technical knowledge and aptitude relevant to the job role.

The assessment score is stored in Snowflake.


Candidates who fail to meet the assessment threshold are rejected automatically.


---

6. Composite Scoring and Shortlisting

For candidates who successfully clear both ATS screening and assessment evaluation:

Resume score

Application data score

Assessment score


are combined using a composite scoring mechanism to calculate a final score.

Only candidates with final scores above the defined threshold are shortlisted.


---

7. Data Storage and Management

All candidate data, scores, job details, and application statuses are stored centrally in the Snowflake database. This ensures data consistency, scalability, and secure access for analytics and reporting.


---

8. HR Visualization and Decision Support

Shortlisted candidate data is visualized using Power BI dashboards.

HR personnel can:

View shortlisted candidates.

Analyze score distributions and performance metrics.

Compare candidates across different evaluation parameters.


This enables HR teams to make faster, data-driven, and unbiased recruitment decisions.


---

9. System Outcome

The system significantly reduces manual screening effort, minimizes human bias, and improves recruitment efficiency by automating resume evaluation, assessment scoring, and candidate ranking.


---

Overall Workflow Summary

> Candidate → Application Submission → ATS Screening → Assessment Evaluation → Composite Scoring → HR Shortlisting


## Software Tools:
Streamlit, Python, Snowflake, Power BI, VS Code, Git hub
