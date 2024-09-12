import streamlit as st
from claude_api import generate_deal_summary
import logging

logging.basicConfig(level=logging.INFO)

def run():
    logging.info("Entered Deal Sourcer stage")

    if "risk_assessments" not in st.session_state:
        st.warning("Please complete the Tech Risk Assessor stage first.")
        return

    curated_startups = st.session_state.analyzed_startups
    
    logging.info(f"Curated startups: {curated_startups}")
    logging.info(f"Risk assessments: {st.session_state.risk_assessments}")

    st.header("Deal Sourcer")
    st.subheader("Curated List of Investment Opportunities")

    for startup in curated_startups:
        risk_assessment = st.session_state.risk_assessments.get(startup['name'], "No risk assessment available")
        risk_score = int(risk_assessment.split('\n')[0])
        with st.expander(f"{startup['name']} (Risk Score: {risk_score})"):
            startup_info = f"""Name: {startup['name']}
Description: {startup.get('description', 'No description available')}
Technology: {startup.get('technology', 'No technology information available')}
Funding: {startup.get('funding', 'N/A')}"""
            deal_summary = generate_deal_summary(startup_info, risk_assessment)
            st.write(deal_summary)
            st.write(f"Full Risk Assessment: {risk_assessment}")

    st.success("You have completed all stages of the DeepTech Startup Deal Sourcing Tool. Use this curated list to inform your investment decisions.")

    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
