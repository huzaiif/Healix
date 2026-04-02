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
    # Beautiful styling for the auth page
    st.markdown("""
        <style>
        /* Hide navbar, header and sidebar completely */
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        
        /* Full height background with modern gradient */
        .stApp {
            background: var(--background-color);
            background-image: radial-gradient(circle at 10% 20%, rgba(67, 97, 238, 0.05) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(76, 201, 240, 0.05) 0%, transparent 40%);
        }
        
        /* Restrict width and center the main container vertically and horizontally. Make IT the card! */
        .block-container {
            max-width: 480px !important;
            padding: 3rem 2.5rem !important;
            margin: 8vh auto !important;
            background-color: var(--secondary-background-color);
            border-radius: 28px;
            box-shadow: 0 15px 45px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(128, 128, 128, 0.15);
        }

        /* Remove the background/shadow styling from the Tabs */
        div[data-testid="stTabs"] {
            background-color: transparent;
            padding: 0;
            border-radius: 0;
            box-shadow: none;
            border: none;
        }

        /* Style the tabs headers */
        button[data-baseweb="tab"] {
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: var(--text-color) !important;
            opacity: 0.6 !important;
            flex: 1 !important;
            justify-content: center !important;
            background-color: transparent !important;
            border-bottom: 2px solid transparent !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            opacity: 1 !important;
            color: #4361ee !important;
            border-bottom-color: #4361ee !important;
        }

        /* Inputs */
        div[data-baseweb="input"] {
            border-radius: 12px !important;
            border: 1px solid rgba(128, 128, 128, 0.2) !important;
            background-color: var(--background-color) !important;
            transition: all 0.2s ease;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #4361ee !important;
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.15) !important;
        }

        /* Form labels */
        .stTextInput label p {
            font-weight: 500 !important;
            color: var(--text-color) !important;
            font-size: 0.95rem !important;
            opacity: 0.8 !important;
        }

        /* Primary Buttons */
        div.stButton > button {
            border-radius: 12px !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            margin-top: 0.5rem;
            background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%) !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(67, 97, 238, 0.2) !important;
            transition: transform 0.2s, box-shadow 0.2s !important;
        }
        div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(67, 97, 238, 0.3) !important;
            color: white !important;
        }
        
        /* Headers inside tabs */
        div[data-testid="stMarkdownContainer"] h3 {
            text-align: center;
            color: var(--text-color);
            font-weight: 700;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
        }
        
        /* Dark mode specific fine-tuning */
        @media (prefers-color-scheme: dark) {
            .block-container {
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                box-shadow: 0 15px 45px rgba(0, 0, 0, 0.4) !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Logo centered
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.image("assets/images/logo.png", use_column_width=True)
    
    st.write("")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.markdown("<h3>Welcome Back 👋</h3>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            if login_user(username, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password")
                
    with tab2:
        st.markdown("<h3>Create Account ✨</h3>", unsafe_allow_html=True)
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
