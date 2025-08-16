from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
import logging
from datetime import datetime
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='fork_detector.log'
)

API_URL = "https://api.llama.fi/protocols"

def process_forks(data: list, min_tvl: float) -> List[Dict]:
    """Filter and process fork data with TVL check"""
    processed = []
    for item in data:
        try:
            tvl_str = str(item.get('tvl', 0)).replace(',', '')
            tvl = float(tvl_str) if tvl_str.replace('.', '').isdigit() else 0
            if item.get('forkedFrom') and tvl >= min_tvl:
                processed.append(item)
        except (ValueError, TypeError, AttributeError):
            continue
    return processed

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True
)
def get_recent_forks(min_tvl: float = 1_000_000) -> List[Dict]:
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        return process_forks(response.json(), min_tvl)
    except requests.exceptions.RequestException as e:
        logging.error(f"API Error @ {datetime.now()}: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error @ {datetime.now()}: {str(e)}")
        return []