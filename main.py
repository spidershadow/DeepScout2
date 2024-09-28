import streamlit as st
from stages import sector_selector, startup_finder, tech_risk_assessor
from database import init_connection
from utils import initialize_session_state
import logging

logging.basicConfig(level=logging.INFO)

def main():
    try:
        st.set_page_config(page_title="DeepScout", layout="wide")
        st.title("DeepScout")

        # Initialize database connection
        conn = init_connection()
        logging.info("Database connection initialized")

        # Initialize session state
        initialize_session_state()
        logging.info("Session state initialized")

        # Main content area
        if st.session_state.current_stage == "Startup Finder":
            startup_finder.run(conn)
        elif st.session_state.current_stage == "Tech Risk Assessor":
            tech_risk_assessor.run()
        else:
            sector_selector.run(conn)

        # Display current stage and progress
        st.sidebar.write(f"Current Stage: {st.session_state.current_stage}")
        st.sidebar.progress(st.session_state.progress)

        logging.info(f"Session state after stage execution: {st.session_state}")
    except Exception as e:
        logging.error(f"An error occurred in the main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again or contact support.")

if __name__ == "__main__":
    main()
