import streamlit as st
from claude_api import assess_tech_risk, generate_startup_insights, generate_portfolio_summary
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
As an AI assistant to a Venture Capital firm, analyze the following tech risk assessment data and provide actionable insights for the General Partners:

```json
{json.dumps(summary_data, indent=2)}
```

Average Risk Score: {avg_risk_score:.2f}

1. Executive Summary (2-3 sentences):
   Concisely outline the overall tech risk landscape, highlighting any critical concerns or opportunities.

2. Key Insights (3 bullet points):
   • [Most significant pattern or trend]
   • [Highest potential risk or area of concern]
   • [Most promising opportunity or strength]

3. Strategic Recommendations (3-4 bullet points):
   • [Immediate action item to address highest risk]
   • [Suggestion to capitalize on identified opportunity]
   • [Recommendation for portfolio balancing or risk mitigation]
   • [Proposed follow-up or due diligence focus]

4. Potential Impact on Returns (1-2 sentences):
   Briefly assess how the identified risks and opportunities might affect potential returns.

Please keep each section concise and focused on information that directly impacts investment decisions and portfolio management.
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

        # Deep Dive Analysis
        st.subheader("Deep Dive Analysis")
        
        while True:
            selected_startup = st.selectbox("Choose a startup for deep dive analysis:", 
                                            [startup['name'] for startup in st.session_state.analyzed_startups])
            
            analysis_area = st.radio("Select an area to analyze:",
                                     ["Regulatory Challenges", "Market Adoption Potential", "Competitive Landscape"])
            
            startup_info = next(startup for startup in st.session_state.analyzed_startups if startup['name'] == selected_startup)
            insights = generate_startup_insights(startup_info, analysis_area)
            
            st.write(f"Insights for {selected_startup} - {analysis_area}:")
            st.write(insights)
            
            action = st.radio("What would you like to do next?",
                              ["Analyze another area for this startup",
                               "Analyze a different startup",
                               "End session and generate portfolio summary"])
            
            if action == "End session and generate portfolio summary":
                break
            elif action == "Analyze a different startup":
                continue

        # Portfolio Summary
        st.subheader("Portfolio Summary")
        summary = generate_portfolio_summary(st.session_state.analyzed_startups)
        st.write(summary)

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
