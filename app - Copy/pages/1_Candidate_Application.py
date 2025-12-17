import streamlit as st
import uuid
import json
import logging
import time
import datetime
from utils.db_connector import SnowflakeConnector
from utils.ats_engine import ATSEngine
from utils.helpers import send_email, logout_button, hide_sidebar

# Configure Logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Candidate Assessment", page_icon="📝", layout="wide")
hide_sidebar()

# Initialize Utilities
db = SnowflakeConnector()
ats = ATSEngine()

# Session State Management for Wizard Steps
if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1 # 1=Apply, 2=Assessment, 3=Chat, 4=Done
if 'assessment_start_time' not in st.session_state:
    st.session_state.assessment_start_time = None

# --- TOKEN LOGIC (Hydrate Session from Link) ---
token = st.query_params.get("token")
if token:
    # 1. Fetch Candidate
    candidate = db.get_candidate_by_id(token)
    if candidate is not None:
        # 2. Security: Check Protocol (Pass ATS)
        if not candidate['ATS_PASS']:
             st.error("Access Denied: Application not shortlisted.")
             st.stop()
        
        # 3. Hydrate Session (Bypass "Select Job" warning)
        job_id = candidate['JOB_ID']
        job_info = db.get_job_details(job_id)
        
        if job_info is not None:
            st.session_state.selected_job_id = job_id
            st.session_state.selected_job_title = job_info['TITLE']
            st.session_state.current_candidate_id = token # Token IS the ID
            st.session_state.role = 'candidate'
            st.session_state.user_name = candidate['NAME']
            
            # 4. Set Wizard Step based on progress
            ass_score = candidate['ASSESSMENT_SCORE']
            
            # Check for None or NaN (Pandas/Snowflake quirk)
            import pandas as pd
            has_score = ass_score is not None and not pd.isna(ass_score)
            
            if has_score:
                 if candidate['CHAT_TRANSCRIPT']:
                     st.session_state.wizard_step = 4
                 else:
                     st.session_state.wizard_step = 3
            else:
                 st.session_state.wizard_step = 2
        else:
             st.error("Associated Job not found.")
             st.stop()
    else:
        st.error("Invalid Assessment Link.")
        st.stop()

# --- REDIRECT LOGIC ---
if 'selected_job_id' not in st.session_state:
    st.warning("Please select a job from the Job Portal first.")
    if st.button("Go to Job Portal"):
        st.switch_page("pages/3_Job_Search.py")
    st.stop()

if st.session_state.get('role'):
    logout_button() # Add Logout

job_id = st.session_state.selected_job_id
job_title = st.session_state.selected_job_title
job_details = db.get_job_details(job_id)

st.title(f"🚀 Application for {job_title}")

def render_application_step():
    st.subheader("Step 1: Application Details")
    
    with st.form("app_form"):
        col1, col2 = st.columns(2)
        with col1:
            pre = st.session_state.get('prefill_data', {})
            name = st.text_input("Full Name", value=pre.get('name', ''))
            email = st.text_input("Email", value=pre.get('email', ''))
            phone = st.text_input("Phone", value=pre.get('phone', ''))
        with col2:
            exp = st.number_input("Years of Experience", 0, 50)
            skills = st.text_area("Key Skills")
            education = st.selectbox("Education", ["B.Tech", "M.Tech", "PhD", "Other"])

        resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        
        submitted = st.form_submit_button("Submit Application")
        
        if submitted:
            if email:
                # 0. Check for existing application
                status = db.get_application_status(email, job_id)
                
                if status is not None:
                    # Application Exists
                    # Ensure we handle the case where they just want the link again
                    
                    ats_pass = status['ATS_PASS']
                    candidate_id = status['CANDIDATE_ID']
                    
                    if ats_pass:
                        st.info("You have already been shortlisted for this position.")
                        
                        # Resend Email Logic
                        link = f"http://localhost:8501/Candidate_Application?token={candidate_id}" 
                        email_success, email_msg = send_email(email, "Assessment Invitation (Resent)", f"Here is your assessment link again: {link}")
                        
                        if email_success:
                            st.success(f"We have resent the assessment link to {email}. Please check your inbox.")
                        else:
                            st.warning(f"Could not send email: {email_msg}")
                            st.error("Since email sending failed, here is your link manually:")
                            st.code(link, language="text")
                            st.markdown(f"[Click Here to Start Assessment]({link})")
                    else:
                        st.error("Your previous application for this job was not shortlisted. You cannot apply again.")
                
                elif resume and name:
                    # New Application
                    # 1. ATS Check
                    text = ats.extract_text_from_pdf(resume)
                    jd_text = job_details['DESCRIPTION'] if job_details is not None else job_title
                    score = ats.calculate_compatibility_score(text, jd_text)
                    
                    # Fetch Dynamic Threshold
                    min_score_required = job_details.get('MIN_ATS_SCORE', 50) 
                    # Handle if None (legacy jobs)
                    if min_score_required is None: min_score_required = 50
                    
                    ats_pass = score >= min_score_required
                    
                    c_id = str(uuid.uuid4())
                    
                    c_data = {
                        'id': c_id, 'job_id': job_id, 'name': name, 'email': email,
                        'phone': phone,
                        'experience': str(exp), 'education': education, 
                        'resume_url': resume.name, # Storing original filename for reference
                        'ats_score': score,
                        'ats_pass': ats_pass, 
                        'details_json': json.dumps({'skills': skills}),
                        'resume_blob': resume.getvalue() # Pass binary data
                    }
                    db.insert_candidate(c_data)
                    
                    if ats_pass:
                        st.success("Application Submitted Successfully!")
                        # Send Email with Token Link
                        link = f"http://localhost:8501/Candidate_Application?token={c_id}" 
                        
                        email_success, email_msg = send_email(email, "Assessment Invitation", f"Congratulations! You have been shortlisted. Please start your assessment using this secure link: {link}")
                        
                        if email_success:
                            st.info(f"An email with the assessment link has been sent to {email}. You must use that link to proceed.")
                        else:
                            st.warning(f"Could not send email: {email_msg}")
                            st.error("Since email sending failed (check server config), here is your link manually:")
                            st.code(link, language="text")
                            st.markdown(f"[Click Here to Start Assessment]({link})")
                        
                    else:
                        st.error("Application Submitted. Thank you for your interest.")
                else:
                    st.error("Please provide Resume and details for new application.")
            else:
                st.error("Email is required.")

def render_assessment_step():
    st.subheader("Step 2: Technical Assessment")
    
    # Security Check: Must have ID
    if 'current_candidate_id' not in st.session_state:
        st.error("Session Invalid. Please use the link from your email.")
        st.stop()

    questions = json.loads(job_details['ASSESSMENT_QUESTIONS']) if job_details is not None and job_details['ASSESSMENT_QUESTIONS'] else []
    
    if not questions:
        st.info("No assessment questions configured for this job. Skipping...")
        if st.button("Proceed"):
            st.session_state.wizard_step = 3
            st.rerun()
        return

    # Timer Logic (Countdown)
    limit_minutes = job_details.get('TIME_LIMIT_MINUTES', 30)
    if limit_minutes is None: limit_minutes = 30 # fallback
    
    if not st.session_state.assessment_start_time:
        st.session_state.assessment_start_time = datetime.datetime.now()
    
    # Calculate timestamps
    start_ts = st.session_state.assessment_start_time.timestamp() * 1000 # ms
    limit_ms = int(limit_minutes) * 60 * 1000
    end_ts = start_ts + limit_ms
    
    # JavaScript for Live Countdown Timer
    timer_html = f"""
        <div style="font-family: sans-serif; font-size: 2rem; font-weight: bold; color: #333; background: #fff3cd; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; border: 1px solid #ffeeba;">
            ⏳ Time Remaining: <span id="timer">--:--</span>
        </div>
        <script>
            var end = {end_ts};
            
            function updateTimer() {{
                var now = new Date().getTime();
                var diff = end - now;
                
                if (diff <= 0) {{
                    document.getElementById("timer").innerHTML = "00:00 - Time's Up!";
                    document.getElementById("timer").style.color = "red";
                    // Optional: trigger submit?
                    return;
                }}
                
                var minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((diff % (1000 * 60)) / 1000);
                
                document.getElementById("timer").innerHTML = 
                    (minutes < 10 ? "0" + minutes : minutes) + ":" + 
                    (seconds < 10 ? "0" + seconds : seconds);
            }}
            setInterval(updateTimer, 1000);
            updateTimer();
        </script>
    """
    import streamlit.components.v1 as components
    components.html(timer_html, height=80)
    
    with st.form("quiz_form"):
        answers = {}
        for q in questions:
            st.write(f"**{q['text']}**")
            answers[str(q['id'])] = st.radio("Select Answer", q['options'], key=q['id'], index=None)
            st.divider()
            
        submitted = st.form_submit_button("Submit Assessment")
        
        # Auto-check time logic on server side
        elapsed = (datetime.datetime.now() - st.session_state.assessment_start_time).total_seconds()
        is_overtime = elapsed > (limit_minutes * 60 + 10) # 10s grace
        
        if submitted:
            if is_overtime:
                st.warning("Time Limit Exceeded! Submission accepted but marked as late.")
                # We can choose to penalize or just accept. 
                # For now just proceed.
            
            # Calc Duration
            end_time = datetime.datetime.now()
            duration_secs = (end_time - st.session_state.assessment_start_time).total_seconds()

            score = 0
            for q in questions:
                if answers[str(q['id'])] == q['answer']:
                    score += 1
            
            final_assessment_score = (score / len(questions)) * 100
            
            # Save Score & Duration
            db.update_candidate_assessment(st.session_state.current_candidate_id, final_assessment_score, int(duration_secs))
            
            st.success(f"Assessment Completed! Score: {final_assessment_score:.1f}%")
            time.sleep(1)
            st.session_state.wizard_step = 3
            st.rerun()

def render_chat_step():
    st.subheader("Step 3: Screening Chat")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Tell me about yourself and your interest in this role."}]
        
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("Your answer..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Simple Logic: Ask 3 questions then finish
        count = len([m for m in st.session_state.messages if m['role'] == 'user'])
        
        if count == 1:
            response = "What are your salary expectations?"
        elif count == 2:
            response = "When can you join?"
        elif count >= 3:
            response = "Thank you! We have recorded your responses. The process is now complete."
            
            # AI Scoring Trigger
            if 'scoring_done' not in st.session_state:
                with st.spinner("AI is evaluating your interview responses..."):
                    import json
                    from utils.ai_screener import evaluate_screening_chat
                    
                    # Fetch Job Desc
                    job_desc = job_details['DESCRIPTION'] if job_details is not None else "General Role"
                    
                    screening_score, summary = evaluate_screening_chat(st.session_state.messages, job_desc)
                    
                    # Log Transcript & Score
                    target_id = st.session_state.current_candidate_id
                    transcript_json = json.dumps(st.session_state.messages)
                    db.update_chat_transcript(target_id, transcript_json, screening_score)
                    
                    # --- FINAL SCORE CALCULATION ---
                    # 1. Get Candidate Data
                    cand = db.get_candidate_by_id(target_id)
                    ats_s = cand['ATS_SCORE'] if cand.get('ATS_SCORE') is not None else 0
                    ass_s = cand['ASSESSMENT_SCORE'] if cand.get('ASSESSMENT_SCORE') is not None else 0
                    
                    # 2. Avg
                    final_score = (ats_s + ass_s + screening_score) / 3
                    
                    # 3. Save
                    db.update_final_score(target_id, final_score)
                    
                    st.session_state.scoring_done = True
            
            st.session_state.wizard_step = 4
            st.rerun()
        else:
            response = "Okay."
            
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

def render_completion_step():
    st.balloons()
    st.success("Application Process Completed Successfully!")
    st.info("You can now close this window.")
    if st.button("Back to Home"):
         st.session_state.wizard_step = 1
         st.switch_page("Home.py")

# Router
if st.session_state.wizard_step == 1:
    render_application_step()
elif st.session_state.wizard_step == 2:
    render_assessment_step()
elif st.session_state.wizard_step == 3:
    render_chat_step()
elif st.session_state.wizard_step == 4:
    render_completion_step()
