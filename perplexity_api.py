import os
import requests
import json
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_perplexity_api_key():
    return bool(PERPLEXITY_API_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_startup_list(sector: str, sub_sector: str, num_startups: int = 5) -> list:
    if not check_perplexity_api_key():
        raise ValueError("Perplexity API key is not set in the environment variables.")

    logging.info(f"Generating startup list for {sector} - {sub_sector} using Perplexity API")

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Search for {num_startups} startups in the {sector} sector focusing on lesser-known companies that are gaining traction, specifically in the {sub_sector} sub-sector. For each startup, provide the following information: name, description, funding amount (if available), and key technology. Format the response as a JSON array of startup objects, each containing 'name', 'description', 'funding', and 'technology' fields."""

    payload = {
        "model": "llama-3.1-sonar-large-128k-online",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        logging.info(f"Raw API response:\n{content}")

        # Extract the JSON array from the response
        json_content = extract_json_array(content)
        startup_list = json.loads(json_content)

        if not isinstance(startup_list, list) or not all(isinstance(item, dict) for item in startup_list):
            raise ValueError("Invalid response format: Not a list of dictionaries")

        logging.info(f"Parsed startup list: {startup_list}")
        return startup_list

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Perplexity API: {e}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error generating startup list: {e}")
        raise

def extract_json_array(content):
    start_index = content.find("[")
    end_index = content.rfind("]") + 1
    if start_index != -1 and end_index != -1:
        return content[start_index:end_index]
    else:
        raise ValueError("Invalid response format: JSON array not found")