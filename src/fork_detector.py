# Updated fork_detector.py
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import requests
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='fork_detector.log'
)

API_URL = "https://api.llama.fi/protocols"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def get_recent_forks(min_tvl: float = 1_000_000) -> List[Dict]:
    """Fetch forks with proper error handling and retries"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return [
            fork for fork in response.json()
            if fork.get('tvl', 0) >= min_tvl
            and fork.get('forkedFrom')
        ]
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
    except ValueError as e:
        logging.error(f"JSON decode error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    return []