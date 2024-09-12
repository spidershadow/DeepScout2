import streamlit as st
from claude_api import generate_claude_response, generate_sector_info
from stages import startup_finder
import logging

logging.basicConfig(level=logging.INFO)

def run(conn):
    st.header("Sector Selector")
    sectors = ["Artificial Intelligence", "Quantum Computing", "Biotechnology", "Renewable Energy", "Nanotechnology"]

    if 'sector_selected' not in st.session_state:
        st.session_state.sector_selected = False
    if 'sector_info' not in st.session_state:
        st.session_state.sector_info = None

    if not st.session_state.sector_selected:
        selected_sector = st.selectbox("Choose a deeptech sector:", sectors)
        if st.button("Confirm Sector"):
            st.session_state.sector_selected = True
            st.session_state.selected_sector = selected_sector
            with st.spinner("Generating sector information..."):
                try:
                    logging.info(f"Generating sector information for {selected_sector}")
                    st.session_state.sector_info = generate_sector_info(selected_sector)
                    logging.info(f"Sector information generated successfully: {st.session_state.sector_info}")
                except Exception as e:
                    logging.error(f"Error generating sector information: {str(e)}")
                    st.error("An error occurred while generating sector information. Please try again.")
                    st.session_state.sector_selected = False
                    st.session_state.sector_info = None
            st.rerun()

    if st.session_state.sector_selected:
        st.subheader(f"{st.session_state.selected_sector} Overview")

        sector_info = st.session_state.sector_info
        if sector_info:
            st.write(sector_info['summary'])
            st.subheader("Sub-sectors")
            for sub_sector, description in sector_info['sub_sectors'].items():
                with st.expander(f"{sub_sector}"):
                    st.write(description)

            selected_sub_sector = st.selectbox("Choose a sub-sector:", list(sector_info['sub_sectors'].keys()), key="sub_sector_select")

            st.write("Please select an option:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Go back to Sector Selection"):
                    st.session_state.sector_selected = False
                    st.session_state.sector_info = None
                    st.rerun()
            with col2:
                if st.button("Proceed to Startup Selection"):
                    logging.info("Proceed to Startup Selection button clicked")
                    st.session_state.selected_sub_sector = selected_sub_sector
                    st.session_state.current_stage = "Startup Finder"
                    st.session_state.progress = 0.5
                    st.success(f"You have selected the {st.session_state.selected_sector} sector and the {selected_sub_sector} sub-sector.")
                    st.info("Proceeding to Startup Selection...")
                    st.rerun()
        else:
            st.error("No sector information available. Please go back and select a sector again.")

    if st.session_state.current_stage == "Startup Finder":
        logging.info("Redirecting to Startup Finder")
        startup_finder.run(conn)
        return
