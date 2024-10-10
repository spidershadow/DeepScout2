import streamlit as st
from perplexity_api import generate_startup_list, check_perplexity_api_key
import logging
from stages import tech_risk_assessor
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_startup_list_with_retry(sector, sub_sector):
    return generate_startup_list(sector, sub_sector)

def run(conn):
    st.header("Startup Finder")

    # Check for API key
    if not check_perplexity_api_key():
        st.error("Perplexity API key is not set. Please set the PERPLEXITY_API_KEY environment variable.")
        return

    # Reset startup-related states
    if 'reset_startup_finder' not in st.session_state:
        st.session_state.reset_startup_finder = True

    if st.session_state.reset_startup_finder:
        keys_to_clear = [
            'startups', 'selected_startups', 'analyzed_startups',
            'startup_selection_confirmed', 'risk_assessments'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.reset_startup_finder = False

    # Check if sector and sub-sector are selected
    if "selected_sector" not in st.session_state or "selected_sub_sector" not in st.session_state:
        st.warning("Please complete the Sector Selector stage first.")
        return

    # Generate startups for selected sector and sub-sector
    if "startups" not in st.session_state:
        with st.spinner("Generating startup list..."):
            try:
                st.session_state.startups = generate_startup_list_with_retry(st.session_state.selected_sector, st.session_state.selected_sub_sector)
                if not st.session_state.startups:
                    st.error("No startups were found. Please try again or choose a different sector/sub-sector.")
                    return
                logging.info(f"Generated {len(st.session_state.startups)} startups")
            except RetryError as e:
                st.error(f"An error occurred while generating the startup list: {str(e)}")
                logging.error(f"Error in startup generation: {str(e)}")
                if st.button("Retry Startup Generation"):
                    if 'startups' in st.session_state:
                        del st.session_state.startups
                    st.rerun()
                return
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                logging.error(f"Unexpected error in startup generation: {str(e)}")
                return

    # Display startups
    st.subheader(f"Startups in {st.session_state.selected_sector} - {st.session_state.selected_sub_sector}")
    st.write(f"Number of startups found: {len(st.session_state.startups)}")

    for index, startup in enumerate(st.session_state.startups):
        with st.expander(f"{index + 1}. {startup.get('name', 'Unnamed Startup')}"):
            st.write(f"Description: {startup.get('description', 'No description available')}")
            st.write(f"Funding: {startup.get('funding', 'N/A')}")
            st.write(f"Technology: {startup.get('technology', 'No technology information available')}")

    # Allow startup selection
    selected_startups = st.multiselect(
        "Select startups for further analysis:",
        options=[startup.get('name', 'Unnamed Startup') for startup in st.session_state.startups],
        key="selected_startups"
    )

    # Confirm Startup Selection button
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

    # Proceed to Tech Risk Assessor button
    if st.session_state.get('startup_selection_confirmed', False):
        if st.button("Proceed to Tech Risk Assessor"):
            logging.info("Proceeding to Tech Risk Assessor")
            logging.info(f"Analyzed startups in session state: {st.session_state.analyzed_startups}")
            st.session_state.current_stage = "Tech Risk Assessor"
            st.session_state.progress = 1
            tech_risk_assessor.run()
            return

    # Logging
    logging.info(f"Current stage: {st.session_state.get('current_stage', 'Unknown')}")
    logging.info(f"Startup selection confirmed: {st.session_state.get('startup_selection_confirmed', False)}")

    # Reset button
    if st.button("Reset Startup Selection"):
        st.session_state.reset_startup_finder = True
        st.rerun()
