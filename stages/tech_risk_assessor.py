import streamlit as st
from claude_api import assess_tech_risk
import logging

logging.basicConfig(level=logging.INFO)

def run():
    try:
        st.header("Tech Risk Assessor")
        logging.info("Entered Tech Risk Assessor stage")

        if "analyzed_startups" not in st.session_state or not st.session_state.analyzed_startups:
            st.warning("Please complete the Startup Finder stage and select startups for analysis first.")
            logging.warning("No analyzed startups found in session state")
            return

        st.subheader("Tech Risk Assessment for Selected Startups")

        for startup in st.session_state.analyzed_startups:
            try:
                st.write(f"Assessing {startup['name']}")
                logging.info(f"Assessing startup: {startup['name']}")
                startup_info = f"Name: {startup['name']}\nDescription: {startup.get('description', 'No description available')}\nTechnology: {startup.get('technology', 'No technology information available')}"
                risk_assessment = assess_tech_risk(startup_info)

                try:
                    risk_score = int(risk_assessment.split('\n')[0])
                except ValueError:
                    logging.error(f"Error parsing risk score for {startup['name']}")
                    risk_score = 0

                st.write(f"Risk Score: {risk_score}/10")

                if 'risk_assessments' not in st.session_state:
                    st.session_state.risk_assessments = {}
                st.session_state.risk_assessments[startup['name']] = risk_assessment
                st.write("Risk Assessment:")
                st.write(risk_assessment)
                logging.info(f"Completed risk assessment for {startup['name']}")
            except Exception as e:
                logging.error(f"Error assessing startup {startup.get('name', 'Unknown')}: {str(e)}")
                st.error(f"An error occurred while assessing {startup.get('name', 'a startup')}. Please try again.")

        # After assessing all startups
        st.subheader("Summary of Startup Risk Assessments")
        summary_data = []
        for startup in st.session_state.analyzed_startups:
            risk_score = int(st.session_state.risk_assessments[startup['name']].split('\n')[0])
            summary_data.append({
                "Name": startup['name'],
                "Risk Score": risk_score,
                "Technology": startup.get('technology', 'N/A')
            })
        
        # Display summary table
        st.table(summary_data)

        # Display overall statistics
        avg_risk_score = sum(item['Risk Score'] for item in summary_data) / len(summary_data)
        st.write(f"Average Risk Score: {avg_risk_score:.2f}")
        st.write(f"Total Startups Assessed: {len(summary_data)}")

        st.success("Tech Risk Assessment completed. Review the summary above for an overview of all assessed startups.")

    except Exception as e:
        logging.error(f"Error in Tech Risk Assessor: {str(e)}")
        st.error("An error occurred in the Tech Risk Assessor stage. Please try again or contact support.")

if __name__ == "__main__":
    run()
