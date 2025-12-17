import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import streamlit as st

def send_email(to_email, subject, body):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        msg = f"MOCK EMAIL TO {to_email}: {body}"
        print(msg)
        return False, "SMTP Credentials missing (Check .env). Mock email printed to console."

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully."
    except Exception as e:
        error_msg = f"Failed to send email: {e}"
        print(error_msg)
        return False, error_msg

def logout_button():
    # Top right Logout button using columns
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("Logout"):
            st.session_state.role = None
            st.session_state.user_id = None
            st.session_state.wizard_step = 1
            st.switch_page("Home.py")

def get_job_options(db_conn):
    # Retrieve jobs from snowflake to populate dropdown
    # Returns list of tuples (id, title)
    if db_conn:
        query = "SELECT JOB_ID, TITLE FROM JOBS"
        df = db_conn.fetch_data(query)
        if not df.empty:
            return list(zip(df['JOB_ID'], df['TITLE']))
    
    # Fallback for demo
    return [("DEMO_001", "Software Engineer (Demo)")]

def hide_sidebar():
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
