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

    st.header("DeepScout: Sector Selector")
    
    sectors = {
        "Artificial Intelligence": {
            "description": "AI technologies including machine learning, natural language processing, and computer vision.",
            "icon": "🧠",
            "color": "#3498db"
        },
        "Quantum Computing": {
            "description": "Development of quantum computers and quantum algorithms.",
            "icon": "⚛️",
            "color": "#9b59b6"
        },
        "Biotechnology": {
            "description": "Application of biology and technology in medicine, agriculture, and industry.",
            "icon": "🧬",
            "color": "#2ecc71"
        },
        "Renewable Energy": {
            "description": "Clean energy technologies including solar, wind, and hydrogen power.",
            "icon": "🌞",
            "color": "#f1c40f"
        },
        "Nanotechnology": {
            "description": "Manipulation of matter on an atomic, molecular, and supramolecular scale.",
            "icon": "🔬",
            "color": "#e74c3c"
        }
    }

    if not st.session_state.sector_selected:
        st.subheader("Choose a DeepTech Sector")
        
        # Use columns to create a grid-like layout
        col1, col2 = st.columns(2)
        
        for i, (sector, info) in enumerate(sectors.items()):
            with col1 if i % 2 == 0 else col2:
                st.markdown(f"""
                <div style='background-color: {info['color']}; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                    <h3 style='color: white;'>{info['icon']} {sector}</h3>
                    <p style='color: white;'>{info['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Select {sector}", key=f"sector_{sector}"):
                    st.session_state.sector_selected = True
                    st.session_state.selected_sector = sector
                    with st.spinner("Generating sector information..."):
                        try:
                            logging.info(f"Generating sector information for {sector}")
                            st.session_state.sector_info = generate_sector_info(sector)
                            logging.info(f"Sector information generated successfully: {st.session_state.sector_info}")
                        except Exception as e:
                            logging.error(f"Error generating sector information: {str(e)}")
                            st.error("An error occurred while generating sector information. Please try again.")
                            reset_sector_selector()
                    st.experimental_rerun()

    if st.session_state.sector_selected:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"{sectors[st.session_state.selected_sector]['icon']} {st.session_state.selected_sector} Overview")
            sector_info = st.session_state.sector_info
            if sector_info:
                st.markdown("### Sector Summary")
                st.info(sector_info['summary'])
                
                st.markdown("### Latest Sector Trends")
                st.success(sector_info['trends'])
                
                st.subheader("Sub-sectors")
                for sub_sector, description in sector_info['sub_sectors'].items():
                    with st.expander(f"{sub_sector}"):
                        st.write(description)

                selected_sub_sector = st.selectbox("Choose a sub-sector:", list(sector_info['sub_sectors'].keys()), key="sub_sector_select")

                if st.button("Find Startups", key="find_startups_button"):
                    st.session_state.selected_sub_sector = selected_sub_sector
                    st.session_state.show_startup_finder = True
                    st.session_state.current_stage = "Startup Finder"
                    st.session_state.progress = 0.66
                    st.success(f"You have selected the {st.session_state.selected_sector} sector and the {selected_sub_sector} sub-sector.")
                    st.info("Finding startups...")
            else:
                st.error("No sector information available. Please go back and select a sector again.")
                reset_sector_selector()

        with col2:
            st.write(" ")
            st.write(" ")
            if st.button("Go back to Sector Selection", key="go_back_button"):
                reset_sector_selector()
                st.experimental_rerun()

    if st.session_state.show_startup_finder:
        startup_finder.run(conn)

    logging.info(f"Current session state: {st.session_state}")
