import streamlit as st
from claude_api import generate_startup_list
import logging
from stages import tech_risk_assessor

logging.basicConfig(level=logging.INFO)

def run(conn):
    st.header("Startup Finder")

    if "selected_sector" not in st.session_state or "selected_sub_sector" not in st.session_state:
        st.warning("Please complete the Sector Selector stage first.")
        return

    # Generate startups for selected sector and sub-sector
    if "startups" not in st.session_state:
        st.session_state.startups = generate_startup_list(st.session_state.selected_sector, st.session_state.selected_sub_sector)

    # Display startups
    st.subheader(f"Startups in {st.session_state.selected_sector} - {st.session_state.selected_sub_sector}")
    for startup in st.session_state.startups:
        with st.expander(startup.get('name', 'Unnamed Startup')):
            st.write(f"Description: {startup.get('description', 'No description available')}")
            st.write(f"Funding: ${startup.get('funding', 'N/A'):,}" if startup.get('funding') else "Funding: N/A")
            st.write(f"Technology: {startup.get('technology', 'No technology information available')}")

    # Allow startup selection without immediate action
    selected_startups = st.multiselect(
        "Select startups for further analysis:",
        options=[startup.get('name', 'Unnamed Startup') for startup in st.session_state.startups],
        key="selected_startups"
    )

    # Add Confirm Startup Selection button
    if st.button("Confirm Startup Selection"):
        if selected_startups:
            st.session_state.analyzed_startups = [
                startup for startup in st.session_state.startups if startup.get('name') in selected_startups
            ]
            st.session_state.startup_selection_confirmed = True
            st.success("Startup selection confirmed!")
            st.info("Please proceed to the Tech Risk Assessor stage.")
            logging.info(f"Selected startups: {selected_startups}")
            logging.info(f"Analyzed startups: {st.session_state.analyzed_startups}")
        else:
            st.warning("Please select at least one startup before confirming.")

    # Add button to proceed to Tech Risk Assessor
    if st.session_state.get('startup_selection_confirmed', False):
        if st.button("Proceed to Tech Risk Assessor"):
            logging.info("Proceeding to Tech Risk Assessor")
            logging.info(f"Analyzed startups in session state: {st.session_state.analyzed_startups}")
            st.session_state.current_stage = "Tech Risk Assessor"
            st.session_state.progress = 0.75
            tech_risk_assessor.run()
            return

    logging.info(f"Current stage: {st.session_state.get('current_stage', 'Unknown')}")
    logging.info(f"Startup selection confirmed: {st.session_state.get('startup_selection_confirmed', False)}")
