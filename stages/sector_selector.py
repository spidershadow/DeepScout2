import streamlit as st
from claude_api import generate_sector_info
import logging
from stages import startup_finder

logging.basicConfig(level=logging.INFO)

def initialize_session_state():
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 'Sector Selector'
    if 'progress' not in st.session_state:
        st.session_state.progress = 0.33
    if 'sector_selected' not in st.session_state:
        st.session_state.sector_selected = False
    if 'sector_info' not in st.session_state:
        st.session_state.sector_info = None
    if 'show_startup_finder' not in st.session_state:
        st.session_state.show_startup_finder = False
    if 'selected_sector' not in st.session_state:
        st.session_state.selected_sector = None
    if 'selected_sub_sector' not in st.session_state:
        st.session_state.selected_sub_sector = None

def reset_sector_selector():
    st.session_state.sector_selected = False
    st.session_state.sector_info = None
    st.session_state.show_startup_finder = False
    st.session_state.selected_sector = None
    st.session_state.selected_sub_sector = None
    st.session_state.current_stage = 'Sector Selector'
    st.session_state.progress = 0.33

def run(conn):
    initialize_session_state()

    st.header("Sector Selector")
    sectors = ["Artificial Intelligence", "Quantum Computing", "Biotechnology", "Renewable Energy", "Nanotechnology"]

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
                    reset_sector_selector()
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

            if st.button("Find Startups"):
                st.session_state.selected_sub_sector = selected_sub_sector
                st.session_state.show_startup_finder = True
                st.session_state.current_stage = "Startup Finder"
                st.session_state.progress = 0.66
                st.success(f"You have selected the {st.session_state.selected_sector} sector and the {selected_sub_sector} sub-sector.")
                st.info("Finding startups...")
        else:
            st.error("No sector information available. Please go back and select a sector again.")
            reset_sector_selector()

        if st.button("Go back to Sector Selection"):
            reset_sector_selector()
            st.rerun()

    if st.session_state.show_startup_finder:
        startup_finder.run(conn)

    logging.info(f"Current session state: {st.session_state}")