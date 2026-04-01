import streamlit as st
import bcrypt
from database.db import authenticate_user as db_authenticate_user, create_user

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_user(username, password):
    user = db_authenticate_user(username)
    if user and check_password(password, user['password_hash']):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user['id']
        st.session_state['username'] = user['username']
        return True
    return False

def register_user(username, email, password):
    hashed_pw = hash_password(password)
    return create_user(username, email, hashed_pw)

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state.pop('user_id', None)
    st.session_state.pop('username', None)
    st.session_state.pop('messages', None)
    st.rerun()

def show_auth_page():
    # Helper styling for the login page
    st.markdown("""
        <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/images/logo.png", use_column_width=True)
        
    st.markdown("<h1 style='text-align: center; margin-top: -20px;'>Hayat</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>Your Complete AI Health Assistant</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Login to your account")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True):
                if login_user(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    
        with tab2:
            st.subheader("Create a new account")
            new_user = st.text_input("Username", key="reg_user")
            new_email = st.text_input("Email", key="reg_email")
            new_pass = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Sign Up", use_container_width=True):
                if new_user and new_email and new_pass:
                    if register_user(new_user, new_email, new_pass):
                        st.success("Account created successfully! You can now login.")
                    else:
                        st.error("Username or email already exists.")
                else:
                    st.warning("Please fill out all fields.")
