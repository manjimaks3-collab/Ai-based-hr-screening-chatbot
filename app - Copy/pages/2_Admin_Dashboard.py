import streamlit as st
import uuid
import pandas as pd
import time
from utils.db_connector import SnowflakeConnector
from utils.scoring_engine import ScoringEngine
from utils.helpers import logout_button, hide_sidebar

st.set_page_config(page_title="Admin Dashboard", page_icon="👔", layout="wide")
hide_sidebar()

if st.session_state.get('role') != 'admin':
    st.error("Access Denied. Please login as Admin.")
    st.stop()

if st.session_state.get('role'):
    logout_button()

st.title("👔 Recruiter Dashboard")

db = SnowflakeConnector()
scorer = ScoringEngine()

tab1, tab2, tab3 = st.tabs(["Manage Jobs", "View Applications", "AI Scoring & Shortlist"])

with tab1:
    st.subheader("Manage Jobs")
    action = st.radio("Action", ["Post New Job", "Edit an Existing Job"], horizontal=True)

    # --- Helper for Question Builder ---
    def render_question_builder(key_prefix, existing_questions=None):
        # Initialize list in session state if needed
        list_key = f"{key_prefix}_q_list"
        if list_key not in st.session_state:
            st.session_state[list_key] = existing_questions if existing_questions else []

        st.markdown("##### ➕ Add Assessment Question")
        c1, c2 = st.columns([3, 1])
        q_text = c1.text_input("Question Text", key=f"{key_prefix}_q_text")
        num_opts = c2.number_input("Options Count", 2, 6, 4, key=f"{key_prefix}_num_opts")
        
        opts = []
        cols = st.columns(num_opts)
        for i in range(num_opts):
            val = cols[i].text_input(f"Option {i+1}", key=f"{key_prefix}_opt_{i}")
            opts.append(val)
        
        # Filter empty options for answer selector
        valid_opts = [o for o in opts if o.strip()]
        if valid_opts:
            ans = st.selectbox("Correct Answer", valid_opts, key=f"{key_prefix}_ans")
        else:
            ans = None
            st.caption("Enter options to select answer.")

        if st.button("Add to List", key=f"{key_prefix}_add_btn"):
            if q_text and len(valid_opts) >= 2 and ans:
                new_q = {
                    "id": len(st.session_state[list_key]) + 1,
                    "text": q_text,
                    "options": opts, # Save all, even empty? Better to save valid only.
                    "answer": ans
                }
                # Clean up options
                new_q['options'] = [o.strip() for o in opts if o.strip()]
                st.session_state[list_key].append(new_q)
                st.success("Question Added!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("Please enter Question text and at least 2 options.")

        # Display Added Questions
        if st.session_state[list_key]:
            st.markdown("##### 📋 Current Questions")
            for i, q in enumerate(st.session_state[list_key]):
                with st.expander(f"{i+1}. {q['text']} (Ans: {q['answer']})"):
                    st.write(f"Options: {', '.join(q['options'])}")
                    if st.button("Remove Question", key=f"{key_prefix}_del_{i}"):
                        st.session_state[list_key].pop(i)
                        st.rerun()
        else:
            st.info("No questions added yet.")
            
        return st.session_state[list_key]

    # --- Mode: Post New Job ---
    if action == "Post New Job":
        title = st.text_input("Job Title")
        desc = st.text_area("Job Description")
        skills = st.text_area("Required Skills (Comma separated)")
        
        st.divider()
        final_questions = render_question_builder("new")
        
        # --- ATS Score Adjustment ---
        min_ats_score = st.slider("Min ATS Match % Required", 0, 100, 50, help="Candidates must match this % to proceed.")
        
        # --- Time Limit Adjustment ---
        time_limit = st.number_input("Assessment Time Limit (Minutes)", min_value=1, max_value=180, value=30, step=1)
        
        if st.button("Post Job", type="primary"):
            if title and desc:
                import json
                job_id = f"JOB_{uuid.uuid4().hex[:8].upper()}"
                
                # Re-index IDs just in case
                for idx, q in enumerate(final_questions):
                    q['id'] = idx + 1
                    
                job_data = {
                    "id": job_id, "title": title, "description": desc,
                    "skills": skills, "questions_json": json.dumps(final_questions),
                    "min_ats_score": min_ats_score,
                    "time_limit": time_limit
                }
                try:
                    db.insert_job(job_data)
                    st.success(f"Job '{title}' Posted Successfully! ID: {job_id}")
                    # Clear session state
                    if 'new_q_list' in st.session_state:
                        del st.session_state['new_q_list']
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error posting job: {e}")
            else:
                st.error("Please fill Job Title and Description.")

    # --- Mode: Edit Existing Job ---
    elif action == "Edit an Existing Job":
        jobs_df = db.fetch_jobs()
        if not jobs_df.empty:
            job_titles = dict(zip(jobs_df['JOB_ID'], jobs_df['TITLE']))
            selected_job_id = st.selectbox("Select Job to Edit", options=jobs_df['JOB_ID'], format_func=lambda x: f"{job_titles[x]} ({x})")
            
            # Helper to manage state reload when job changes
            if 'last_edit_job' not in st.session_state or st.session_state.last_edit_job != selected_job_id:
                 st.session_state.last_edit_job = selected_job_id
                 # Clear previous q list to force reload
                 if 'edit_q_list' in st.session_state:
                     del st.session_state['edit_q_list']

            # Fetch details
            job_details = jobs_df[jobs_df['JOB_ID'] == selected_job_id].iloc[0]
            
            # Parse existing questions once
            existing_qs = []
            if 'edit_q_list' not in st.session_state:
                import json
                try:
                    if job_details['ASSESSMENT_QUESTIONS']:
                        existing_qs = json.loads(job_details['ASSESSMENT_QUESTIONS'])
                except:
                    existing_qs = []

            new_title = st.text_input("Job Title", value=job_details['TITLE'])
            new_desc = st.text_area("Job Description", value=job_details['DESCRIPTION'])
            new_skills = st.text_area("Required Skills", value=job_details['REQUIRED_SKILLS'])
            
            st.divider()
            final_questions = render_question_builder("edit", existing_questions=existing_qs)
            
            # --- ATS Score & Time Limit Adjustment for Existing Jobs ---
            # Fetch existing or default
            curr_min = job_details.get('MIN_ATS_SCORE', 50)
            if curr_min is None: curr_min = 50
            new_min_ats = st.slider("Min ATS Match % Required", 0, 100, int(curr_min), key="edit_ats_min")
            
            curr_time = job_details.get('TIME_LIMIT_MINUTES', 30)
            if curr_time is None: curr_time = 30
            new_time_limit = st.number_input("Assessment Time Limit (Minutes)", min_value=1, max_value=180, value=int(curr_time), step=1, key="edit_time_limit")
            
            c1, c2 = st.columns([1,1])
            with c1:
                if st.button("Update Job", type="primary"):
                    import json
                    # Re-index
                    for idx, q in enumerate(final_questions):
                        q['id'] = idx + 1
                        
                    job_data = {
                        "id": selected_job_id, "title": new_title, "description": new_desc,
                        "skills": new_skills, "questions_json": json.dumps(final_questions),
                        "min_ats_score": new_min_ats,
                        "time_limit": new_time_limit
                    }
                    try:
                        db.update_job(job_data)
                        st.success("Job Updated Successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating: {e}")
            
            with c2:
                 if st.button("DELETE JOB", type="secondary"):
                      st.session_state.confirm_delete = True
            
            if st.session_state.get('confirm_delete'):
                st.warning("Are you sure? This cannot be undone.")
                if st.button("Yes, Delete Permanently"):
                    try:
                        db.delete_job(selected_job_id)
                        st.success("Job Deleted.")
                        st.session_state.confirm_delete = False
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {e}")
        else:
            st.info("No jobs to edit.")


with tab2:
    st.subheader("Candidate Leaderboard")
    
    # Refresh button
    if st.button("Refresh Data"):
        st.rerun()
        
    candidates_df = db.fetch_all_candidates()
    
    if not candidates_df.empty:
        # Key Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Applications", len(candidates_df))
        col2.metric("Shortlisted (ATS Passed)", len(candidates_df[candidates_df['ATS_PASS'] == True]))
        avg_score = candidates_df['ATS_SCORE'].mean()
        col3.metric("Avg ATS Score", f"{avg_score:.1f}")
        
        # Filters
        st.markdown("### Filter Candidates")
        min_score = st.slider("Min ATS Score", 0, 100, 50)
        filtered_df = candidates_df[candidates_df['ATS_SCORE'] >= min_score]
        
        st.dataframe(filtered_df)
        
        # Simple Visualization
        st.bar_chart(filtered_df['ATS_SCORE'])
    else:
        st.info("No applications received yet.")

with tab3:
    st.subheader("Results and Contact Info")
    st.caption("Simplified view for contacting top candidates.")
    
    candidates = db.fetch_all_candidates()
    if not candidates.empty:
        # Filter and Sort already handled by DB fetch
        
        # Select specific columns
        # Check columns existence safety
        # Select specific columns
        # Check columns existence safety
        cols_to_show = ['CANDIDATE_ID', 'NAME', 'EMAIL', 'PHONE', 'ATS_SCORE', 'ASSESSMENT_SCORE', 'SCREENING_SCORE', 'FINAL_SCORE', 'ATS_PASS', 'RESUME_URL']
        final_cols = [c for c in cols_to_show if c in candidates.columns]
        
        display_df = candidates[final_cols].copy()
        
        # Formatting (Optional)
        st.dataframe(
            display_df.style.format({
                'ATS_SCORE': "{:.1f}", 
                'ASSESSMENT_SCORE': "{:.1f}",
                'SCREENING_SCORE': "{:.1f}",
                'FINAL_SCORE': "{:.1f}"
            }),
            use_container_width=True
        )
        
        st.divider()
        st.subheader("📄 View Resumes")
        st.divider()
        st.markdown("### 📄 View & Download Resumes")
        
        # Helper to get name for dropdown
        def get_cand_label(row):
            return f"{row['NAME']} ({row['EMAIL']})"
            
        cand_options = display_df.to_dict('records')
        
        if cand_options:
            selected_cand = st.selectbox(
                "Select Candidate to Download Resume", 
                cand_options, 
                format_func=get_cand_label
            )
            
            if selected_cand:
                # Fetch full resume data (BLOB) from DB
                c_id = selected_cand['CANDIDATE_ID']
                resume_record = db.get_candidate_resume(c_id)
                
                if resume_record is not None:
                    # Check for BLOB data first
                    blob_data = resume_record.get('RESUME_DATA')
                    # Get authoritative filename from DB record, not UI selection
                    db_filename = resume_record.get('RESUME_URL')
                    
                    # Backward compatibility for file system
                    if blob_data:
                        st.download_button(
                            label=f"Download {selected_cand['NAME']}'s Resume",
                            data=blob_data,
                            file_name=db_filename if db_filename else 'resume.pdf',
                            mime="application/pdf"
                        )
                    else:
                        # Fallback to local file check (Legacy)
                        import os
                        fname = db_filename
                        if fname:
                             fpath = os.path.join("data/resumes", fname)
                             if os.path.exists(fpath):
                                 with open(fpath, "rb") as f:
                                     st.download_button(
                                        label="Download (Legacy Local)",
                                        data=f,
                                        file_name=fname,
                                        mime="application/pdf"
                                     )
                             else:
                                 st.warning(f"Resume file '{fname}' not found in DB or Disk.")
                        else:
                            st.info("No resume associated with this candidate.")
    else:
        st.info("No candidates found.")

# --- DANGER ZONE (SIDEBAR) ---
with st.sidebar:
    st.divider()
    st.subheader("⚠️ Danger Zone")
    
    if st.button("🗑️ CLEAR ALL DATA", type="primary", help="Permanently delete all candidates and jobs."):
        st.session_state.confirm_wipe = True
        
    if st.session_state.get('confirm_wipe'):
        st.error("❗ This will wipe ALL database records! Irreversible.")
        c1, c2 = st.columns(2)
        if c1.button("✅ YES", use_container_width=True):
            try:
                db.clear_all_data()
                st.toast("Database Wiped Successfully!", icon="🗑️")
                st.session_state.confirm_wipe = False
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        
        if c2.button("❌ NO", use_container_width=True):
            st.session_state.confirm_wipe = False
            st.rerun()

    st.divider()
    if st.button("🛠️ INITIALIZE DATABASE", help="Creates missing tables (Safe to run multiple times)."):
        try:
            db.init_db()
            st.success("Database Initialized!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Init Failed: {e}")



