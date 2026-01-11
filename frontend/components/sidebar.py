import streamlit as st
from streamlit_option_menu import option_menu

def create_sidebar():
    with st.sidebar:
        # Logo and Title
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/744/744465.png", width=50)
        with col2:
            st.markdown("<h2 style='margin:0;'>CarLease Pro</h2>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation Menu
        selected = option_menu(
            menu_title="Main Menu",
            options=["Dashboard", "Browse Cars", "Lease Calculator", "My Contracts", "Profile"],
            icons=["house", "car-front", "calculator", "file-text", "person"],
            menu_icon="menu-button-wide",
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "rgba(255,255,255,0.1)"},
                "icon": {"color": "white", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "3px",
                    "padding": "10px",
                    "border-radius": "5px"
                },
                "nav-link-selected": {
                    "background-color": "#3b82f6",
                    "color": "white"
                },
            }
        )
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Cars", "24", "+3")
        with col2:
            st.metric("Leases", "18", "+2")
        
        st.markdown("---")
        
        # User Profile
        st.markdown("### 👤 User Profile")
        st.write("**Name:** John Doe")
        st.write("**Member Since:** Jan 2024")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.markdown("---")
        st.caption("© 2024 CarLease Pro. All rights reserved.")
    
    return selected