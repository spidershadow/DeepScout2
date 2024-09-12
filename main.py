import streamlit as st
from stages import sector_selector, startup_finder, tech_risk_assessor
from database import init_connection
from utils import initialize_session_state
import logging

logging.basicConfig(level=logging.INFO)

def main():
    try:
        st.set_page_config(page_title="DeepTech Startup Deal Sourcing Tool", layout="wide")
        st.title("DeepTech Startup Deal Sourcing Tool")

        # Initialize database connection
        conn = init_connection()
        logging.info("Database connection initialized")

        # Initialize session state
        initialize_session_state()
        logging.info("Session state initialized")

        # Sidebar for navigation
        st.sidebar.title("Navigation")
        stage = st.sidebar.radio("Select Stage", ["Sector Selector", "Startup Finder", "Tech Risk Assessor"])

        # Main content area
        logging.info(f"Current stage: {stage}")
        try:
            if stage == "Sector Selector":
                sector_selector.run(conn)
            elif stage == "Startup Finder":
                startup_finder.run(conn)
            elif stage == "Tech Risk Assessor":
                tech_risk_assessor.run()

            # Check if we need to transition to the next stage
            if st.session_state.get('transition_to_next_stage'):
                st.session_state.current_stage = st.session_state.get('next_stage')
                del st.session_state['transition_to_next_stage']
                del st.session_state['next_stage']
                st.rerun()

        except Exception as stage_error:
            logging.error(f"Error in {stage} stage: {str(stage_error)}")
            st.error(f"An error occurred in the {stage} stage. Please try again or contact support.")

        # Display current stage and progress
        st.sidebar.write(f"Current Stage: {st.session_state.current_stage}")
        st.sidebar.progress(st.session_state.progress)

        logging.info(f"Session state after stage execution: {st.session_state}")
    except Exception as e:
        logging.error(f"An error occurred in the main function: {str(e)}")
        st.error("An unexpected error occurred. Please try again or contact support.")

if __name__ == "__main__":
    main()
