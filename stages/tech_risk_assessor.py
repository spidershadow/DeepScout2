import streamlit as st
from claude_api import assess_tech_risk, generate_claude_response
import logging
import json
from tenacity import retry, stop_after_attempt, wait_fixed


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_risk_assessment(startup_info):
    return assess_tech_risk(startup_info)

def reset_sector_selector():
    st.session_state.sector_selected = False
    st.session_state.sector_info = None
    st.session_state.show_startup_finder = False
    st.session_state.selected_sector = None
    st.session_state.selected_sub_sector = None
    st.session_state.current_stage = 'Tech Risk Assessor'
    st.session_state.progress = 1.00

def parse_risk_score(risk_assessment):
    try:
        for line in risk_assessment.split('\n'):
            if line.startswith("Overall Risk Score:"):
                return float(line.split(":")[1].strip())
        raise ValueError("Risk score not found in assessment")
    except Exception as e:
        logging.error(f"Error parsing risk score: {str(e)}")
        return None

def generate_gp_summary_and_next_steps(summary_data, avg_risk_score):
    prompt = f"""
As an AI assistant to a Venture Capital firm, provide a detailed summary and next steps for the General Partners based on the following tech risk assessment data:

Summary of assessed startups:
{json.dumps(summary_data, indent=2)}

Average Risk Score: {avg_risk_score:.2f}

Please provide:
1. A concise summary of the overall tech risk landscape for these startups (2-3 sentences)
2. Key insights or patterns observed across the assessed startups (3-4 bullet points)
3. Recommended next steps for the General Partners (4-5 bullet points)

Format your response as follows:

Summary:
[Your summary here]

Key Insights:
• [Insight 1]
• [Insight 2]
• [Insight 3]

Recommended Next Steps:
• [Step 1]
• [Step 2]
• [Step 3]
• [Step 4]
• [Step 5]
"""
    return generate_claude_response(prompt)

def run():
    # Reset tech risk assessment related states
    if 'reset_tech_risk_assessor' not in st.session_state:
        st.session_state.reset_tech_risk_assessor = True

    if st.session_state.reset_tech_risk_assessor:
        keys_to_clear = ['risk_assessments', 'gp_summary']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.reset_tech_risk_assessor = False

    try:
        st.header("Tech Risk Assessor")
        logging.info("Entered Tech Risk Assessor stage")

        if "analyzed_startups" not in st.session_state or not st.session_state.analyzed_startups:
            st.warning("Please complete the Startup Finder stage and select startups for analysis first.")
            logging.warning("No analyzed startups found in session state")
            return

        st.subheader("Tech Risk Assessment for Selected Startups")

        if 'risk_assessments' not in st.session_state:
            st.session_state.risk_assessments = {}

        for startup in st.session_state.analyzed_startups:
            try:
                startup_name = startup['name']
                st.write(f"Assessing {startup_name}")
                logging.info(f"Assessing startup: {startup_name}")

                startup_info = json.dumps({
                    "name": startup_name,
                    "description": startup.get('description', 'No description available'),
                    "technology": startup.get('technology', 'No technology information available')
                })

                if startup_name not in st.session_state.risk_assessments:
                    risk_assessment = get_risk_assessment(startup_info)
                    st.session_state.risk_assessments[startup_name] = risk_assessment
                else:
                    risk_assessment = st.session_state.risk_assessments[startup_name]

                risk_score = parse_risk_score(risk_assessment)

                if risk_score is not None:
                    st.write(f"Risk Score: {risk_score:.1f}/10")
                else:
                    st.write("Risk Score: Unable to determine")

                st.write("Risk Assessment:")
                st.text(risk_assessment)
                logging.info(f"Completed risk assessment for {startup_name}")

            except Exception as e:
                logging.error(f"Error assessing startup {startup_name}: {str(e)}")
                st.error(f"An error occurred while assessing {startup_name}. Please try again.")

        # Summary of Startup Risk Assessments
        st.subheader("Summary of Startup Risk Assessments")
        summary_data = []
        for startup in st.session_state.analyzed_startups:
            startup_name = startup['name']
            risk_score = parse_risk_score(st.session_state.risk_assessments[startup_name])
            summary_data.append({
                "Name": startup_name,
                "Risk Score": risk_score if risk_score is not None else "N/A",
                "Technology": startup.get('technology', 'N/A')
            })

        # Display summary table
        st.table(summary_data)
      
        
        # Display overall statistics
        valid_scores = [item['Risk Score'] for item in summary_data if item['Risk Score'] != "N/A"]
        if valid_scores:
            avg_risk_score = sum(valid_scores) / len(valid_scores)
            st.write(f"Average Risk Score: {avg_risk_score:.2f}")
        else:
            st.write("Average Risk Score: Unable to calculate")
            avg_risk_score = None

        st.write(f"Total Startups Assessed: {len(summary_data)}")

        # Generate and display GP summary and next steps
        st.subheader("Detailed Summary and Next Steps for General Partners")
        with st.spinner("Generating insights and recommendations..."):
            gp_summary = generate_gp_summary_and_next_steps(summary_data, avg_risk_score)
            st.markdown(gp_summary)

        st.success("Tech Risk Assessment completed. Review the summary and recommendations above for an overview of all assessed startups.")

        # Add a button to reset and start over
        if st.button("Reset Tech Risk Assessment"):
            st.session_state.reset_tech_risk_assessor = True
            st.rerun()

    except Exception as e:
        logging.error(f"Error in Tech Risk Assessor: {str(e)}")
        st.error("An error occurred in the Tech Risk Assessor stage. Please try again or contact support.")

if __name__ == "__main__":
    run()