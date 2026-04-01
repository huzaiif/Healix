import streamlit as st
from streamlit_option_menu import option_menu
from auth.auth import show_auth_page, logout_user
from utils.helpers import load_css

# Set page configuration MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Hayat", layout="wide", page_icon="assets/images/logo.png")

# Pages imports
from pages.dashboard import show_dashboard
from pages.chat import show_chat
from pages.profile import show_profile
from pages.recommendations import show_recommendations
from pages.reports import show_reports
from pages.history import show_history

def main():
    # Load custom CSS
    load_css()
    
    # Initialize session state for login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        show_auth_page()
    else:
        # Sidebar for navigation
        with st.sidebar:
            st.image("assets/images/logo.png", use_column_width=True)
            st.markdown(f"### 👋 Welcome, {st.session_state['username']}")
            
            selected = option_menu(
                'Menu',
                ['Dashboard', 'Health Profile', 'Chatbot', 'Chat History', 'Recommendations', 'Reports'],
                icons=['house', 'person', 'chat-dots', 'clock-history', 'activity', 'file-earmark-medical'],
                menu_icon='hospital-fill',
                default_index=0
            )
            
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                logout_user()

        # Route to the selected page
        if selected == "Dashboard":
            show_dashboard()
        elif selected == "Health Profile":
            show_profile()
        elif selected == "Chatbot":
            show_chat()
        elif selected == "Chat History":
            show_history()
        elif selected == "Recommendations":
            show_recommendations()
        elif selected == "Reports":
            show_reports()

if __name__ == "__main__":
    main()
