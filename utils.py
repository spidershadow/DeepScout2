import streamlit as st

def initialize_session_state():
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = "Sector Selector"
    if "progress" not in st.session_state:
        st.session_state.progress = 0.25
