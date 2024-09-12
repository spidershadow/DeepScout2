import os
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY environment variable is not set")
anthropic = Anthropic(api_key=CLAUDE_API_KEY)

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
        print(f"Error generating Claude response: {e}")
        return "I apologize, but I'm having trouble generating a response at the moment. Please try again later."

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_claude_response_with_retry(prompt: str, max_tokens: int = 2000) -> str:
    return generate_claude_response(prompt, max_tokens)

def generate_sector_info(sector: str) -> dict:
    prompt = f"""Provide a summary of the {sector} sector and list 5 sub-sectors with brief descriptions."""
    response = generate_claude_response(prompt)

    # Parse the response to extract summary and sub-sectors
    lines = response.split('\n')
    summary = lines[0].strip()
    sub_sectors = {}

    for line in lines[1:]:
        if ':' in line:
            sub_sector, description = line.split(':', 1)
            sub_sectors[sub_sector.strip()] = description.strip()

    return {
        'summary': summary,
        'sub_sectors': sub_sectors
    }

def generate_sector_questions():
    prompt = "Generate 3 questions to help a GP identify promising deeptech sectors for investment."
    return generate_claude_response(prompt)

def analyze_startup(startup_info):
    prompt = f"Analyze the following startup and provide a brief summary of its potential and risks:\n\n{startup_info}"
    return generate_claude_response(prompt)

def assess_tech_risk(startup_info):
    prompt = f'''
    Based on the following startup information, assess the technological risk:

    Startup Information:
    {startup_info}

    Provide a risk score as a single number from 1 to 10 (1 being lowest risk, 10 being highest risk), followed by a brief explanation.
    Format your response as follows:
    <score>
    <explanation>
    '''
    response = generate_claude_response(prompt)
    
    try:
        lines = response.strip().split('\n', 1)
        risk_score = int(lines[0])
        explanation = lines[1] if len(lines) > 1 else ""
        return f"{risk_score}\n{explanation}"
    except ValueError:
        print(f"Error parsing risk score from response: {response}")
        return "0\nError: Unable to generate a valid risk score."

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

def generate_startup_list(sector: str, sub_sector: str, num_startups: int = 5) -> list:
    print(f"Generating startup list for {sector} - {sub_sector}")
    prompt = f"Search for {num_startups} real-world startups in the {sector} sector, specifically in the {sub_sector} sub-sector. For each startup, provide the following information: name, description, funding amount (if available), and key technology. Format the response as a Python list of dictionaries, with each dictionary representing a startup."

    try:
        response = generate_claude_response_with_retry(prompt)
        print(f"Raw API response:\n{response}")

        # Remove any leading or trailing whitespace and newlines
        response = response.strip()

        # Remove any text before the start of the list
        start_index = response.find("[")
        if start_index != -1:
            response = response[start_index:]

        # Remove any text after the end of the list
        end_index = response.rfind("]")
        if end_index != -1:
            response = response[:end_index+1]

        startup_list = eval(response)
        if not isinstance(startup_list, list) or not all(isinstance(item, dict) for item in startup_list):
            raise ValueError("Invalid response format")
        print(f"Parsed startup list: {startup_list}")
        return startup_list
    except Exception as e:
        print(f"Error generating or parsing startup list: {e}")
        print(f"Problematic response: {response}")
        return []
