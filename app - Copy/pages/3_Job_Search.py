import streamlit as st
from utils.db_connector import SnowflakeConnector
from utils.helpers import logout_button, get_job_options, hide_sidebar

st.set_page_config(page_title="Job Portal", page_icon="💼", layout="wide")
hide_sidebar()

if 'role' not in st.session_state or st.session_state.role != 'candidate':
    # Allow browsing without login? Req says they should login then find jobs.
    if st.session_state.get('role') != 'candidate':
         st.warning("Please Login as Candidate to Apply.")
         # Optional: st.stop() if we want to force login just to see jobs.
         # For now, let them see jobs but prompt login on apply.

if st.session_state.get('role'):
    logout_button() 

st.title("💼 Open Positions")

db = SnowflakeConnector()
jobs_df = db.fetch_jobs()

if not jobs_df.empty:
    for index, row in jobs_df.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(row['TITLE'])
                st.markdown(f"**Job ID:** {row['JOB_ID']}")
                st.write(row['DESCRIPTION'])
                st.write(f"**Skills:** {row['REQUIRED_SKILLS']}")
            with col2:
                if st.button(f"Apply Now", key=row['JOB_ID']):
                    if st.session_state.get('role') == 'candidate':
                        st.session_state.selected_job_id = row['JOB_ID']
                        st.session_state.selected_job_title = row['TITLE']
                        st.switch_page("pages/1_Candidate_Application.py")
                    else:
                        st.error("Please Login first!")
            st.divider()
else:
    st.info("No open positions currently.")
