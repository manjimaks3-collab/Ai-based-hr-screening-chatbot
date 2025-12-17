import streamlit as st
import time
from utils.db_connector import SnowflakeConnector
from utils.helpers import logout_button, hide_sidebar

hide_sidebar()

st.set_page_config(
    page_title="HR Screening Bot",
    page_icon="🤖",
    layout="wide"
)
st.title("HR Screening Bot")
st.caption("Welcome to the HR Screening Bot!")
# Initialize Session State
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def login():
    st.title("🔐 Login Portal")
    
    # Single Login Tab
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    db = SnowflakeConnector()
    
    # Auto-Initialize Database (Once per session/run roughly)
    if 'db_initialized' not in st.session_state:
        try:
            db.init_db()
            st.session_state.db_initialized = True
            # print("DB Initialized") 
        except Exception as e:
            st.error(f"DB Init Error: {e}")

    with tab1:
        st.subheader("Welcome Back")
        st.caption("Please login to continue.")
        
        # Unified Inputs
        identifier = st.text_input("Email or Username", key="login_id")
        secret = st.text_input("Password or Phone Number", type="password", key="login_secret")
        
        if st.button("Login"):
            if identifier and secret:
                # 1. Try Admin Login
                if db.authenticate_admin(identifier, secret):
                    st.session_state.role = 'admin'
                    st.session_state.user_id = identifier
                    st.success("Admin Login Successful!")
                    time.sleep(1)
                    st.rerun()
                
                # 2. Try Candidate Login
                # Note: Candidate auth expects (email, phone). 
                # We assume identifier=email, secret=phone
                # We can also check if identifier looks like email?
                else:
                    user = db.authenticate_candidate(identifier, secret)
                    if user is not None:
                        st.session_state.role = 'candidate'
                        st.session_state.user_id = user['CANDIDATE_ID']
                        st.session_state.user_name = user['NAME']
                        # Pre-fill form data if available? 
                        # Actually Application page asks for details again usually,
                        # but we can store them in session to prefill.
                        st.session_state.prefill_data = {
                            'name': user['NAME'],
                            'email': user['EMAIL'],
                            'phone': user['PHONE']
                        }
                        st.success(f"Welcome back, {user['NAME']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid Credentials. Please check your username/password or register.")
            else:
                 st.warning("Please enter credentials.")

    with tab2:
        st.subheader("New Candidate Registration")
        st.write("Please register to access the application form.")
        
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_phone = st.text_input("Phone", key="reg_phone")
        
        if st.button("Register"):
            if reg_name and reg_email and reg_phone:
                try:
                    success = db.register_candidate(reg_name, reg_email, reg_phone)
                    if success:
                        st.success("Registration Successful!")
                        st.info("Please switch to the **Login** tab and sign in with your credentials.")
                    else:
                        st.warning("User already exists. Please Login.")
                except Exception as e:
                    st.error(f"Registration Failed: {e}")
            else:
                st.error("Please fill all details to register.")

def main():
    if st.session_state.role:
        st.sidebar.write(f"Logged in as: **{st.session_state.role.title()}**")
        logout_button() # Add logout here as well logic
            
        if st.session_state.role == 'admin':
            st.switch_page("pages/2_Admin_Dashboard.py")
        elif st.session_state.role == 'candidate':
            # Redirect to a status page or reused application page logic
            st.switch_page("pages/1_Candidate_Application.py")
    else:
        login()

if __name__ == "__main__":
    main()
