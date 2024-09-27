import os
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import logging

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY environment variable is not set")

anthropic = Anthropic(api_key=CLAUDE_API_KEY)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_claude_response(prompt: str, max_tokens: int = 4000) -> str:
    try:
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        logging.error(f"Error generating Claude response: {e}")
        return "I apologize, but I'm having trouble generating a response at the moment. Please try again later."

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_claude_response_with_retry(prompt: str, max_tokens: int = 2000) -> str:
    return generate_claude_response(prompt, max_tokens)

def assess_tech_risk(startup_info_json: str):
    try:
        startup_info = json.loads(startup_info_json)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding startup info JSON: {e}")
        return "Error: Invalid startup information format. Please provide valid JSON."

    startup_name = startup_info.get('name', 'Unknown Startup')
    startup_description = startup_info.get('description', 'No description available')
    startup_technology = startup_info.get('technology', 'No technology information available')

    prompt = f'''
Based on the following startup information, assess the technological risk:

Startup Name: {startup_name}
Description: {startup_description}
Technology: {startup_technology}

Provide your assessment in the following strict format:

1. Technology Novelty: [Low/Medium/High]
Explanation: [1 sentence explanation]

2. Development Stage: [Early/Mid/Late]
Explanation: [1 sentence explanation]

3. Market Potential: [Low/Medium/High]
Explanation: [1 sentence explanation]

4. Competition: [Low/Medium/High]
Explanation: [1 sentence explanation]

5. Regulatory Risk: [Low/Medium/High]
Explanation: [1 sentence explanation]

Overall Risk Score: [1-10]

Summary: [2-3 sentence summary of key risk factors]

Confidence: [Low/Medium/High]

Note: If information is not available for any category, use "Unknown" for the risk level and "Insufficient information" for the explanation.
'''
    try:
        response = generate_claude_response_with_retry(prompt)
    except Exception as e:
        logging.error(f"Error generating risk assessment for {startup_name}: {e}")
        return f"Error: Unable to generate risk assessment for {startup_name}. Please try again later."

    try:
        # Parse the response
        lines = response.split('\n')
        parsed_response = {}
        current_category = ""

        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    current_category = parts[0].split('.')[1].strip()
                    risk_level = parts[1].strip()
                    parsed_response[current_category] = {"risk": risk_level}
            elif line.startswith('Explanation:'):
                if current_category:
                    parsed_response[current_category]["explanation"] = line.split(':', 1)[1].strip()
            elif line.startswith('Overall Risk Score:'):
                try:
                    parsed_response["Overall Risk Score"] = float(line.split(':')[1].strip())
                except ValueError:
                    parsed_response["Overall Risk Score"] = "Unable to parse"
            elif line.startswith('Summary:'):
                parsed_response["Summary"] = line.split(':', 1)[1].strip()
            elif line.startswith('Confidence:'):
                parsed_response["Confidence"] = line.split(':')[1].strip()

        # Construct the formatted response
        formatted_response = f"Technology Risk Assessment for {startup_name}:\n\n"
        for category in ["Technology Novelty", "Development Stage", "Market Potential", "Competition", "Regulatory Risk"]:
            if category in parsed_response:
                formatted_response += f"{category}: {parsed_response[category]['risk']}\n"
                formatted_response += f"Explanation: {parsed_response[category].get('explanation', 'No explanation provided')}\n\n"
            else:
                formatted_response += f"{category}: Unknown\n"
                formatted_response += f"Explanation: Information not provided\n\n"

        formatted_response += f"Overall Risk Score: {parsed_response.get('Overall Risk Score', 'Unable to calculate')}\n\n"
        formatted_response += f"Summary: {parsed_response.get('Summary', 'No summary provided')}\n\n"
        formatted_response += f"Confidence: {parsed_response.get('Confidence', 'Unknown')}"

        return formatted_response

    except Exception as e:
        logging.error(f"Error parsing risk assessment response for {startup_name}: {e}")
        return f"Error: Unable to generate a valid risk assessment for {startup_name}. Please check the API response format."

def generate_sector_info(sector: str) -> dict:
    prompt = f'''Provide information about the {sector} sector in the following format:
    Summary: [A brief summary of the sector]
    Trends: [Latest trends relevant to startup opportunities]
    Sub-sectors:
    1. [Sub-sector name]: [Brief description]
    2. [Sub-sector name]: [Brief description]
    3. [Sub-sector name]: [Brief description]
    4. [Sub-sector name]: [Brief description]
    5. [Sub-sector name]: [Brief description]
    '''
    response = generate_claude_response(prompt)
    
    # Parse the response
    parts = response.split('Sub-sectors:')
    main_info = parts[0].strip().split('Trends:')
    summary = main_info[0].replace('Summary:', '').strip()
    trends = main_info[1].strip() if len(main_info) > 1 else ''
    
    sub_sectors = {}
    if len(parts) > 1:
        sub_sector_lines = parts[1].strip().split('\n')
        for line in sub_sector_lines:
            if ':' in line:
                name, description = line.split(':', 1)
                sub_sectors[name.strip()] = description.strip()
    
    return {
        'summary': summary,
        'trends': trends,
        'sub_sectors': sub_sectors
    }

def generate_sector_questions():
    prompt = "Generate 3 questions to help a GP identify promising deeptech sectors for investment."
    return generate_claude_response(prompt)

def analyze_startup(startup_info):
    prompt = f"Analyze the following startup and provide a brief summary of its potential and risks:\n\n{startup_info}"
    return generate_claude_response(prompt)

def generate_deal_summary(startup_info, risk_assessment):
    prompt = f"""
Create a concise deal summary for the following startup, including its potential and risk assessment:

Startup Information:
{startup_info}

Risk Assessment:
{risk_assessment}

Provide a summary in 3-4 sentences, highlighting key points for a GP to consider.
"""
    return generate_claude_response(prompt)
