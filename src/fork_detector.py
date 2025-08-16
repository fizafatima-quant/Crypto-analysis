# src/fork_detector.py
from typing import List, Dict
import requests

def get_recent_forks(min_tvl: float = 1_000_000) -> List[Dict]:
    """
    Findet neue DEX-Forks (Uniswap-basiert)

    Args:
        min_tvl: Mindest-Total Value Locked in USD (Standard: 1.000.000)

    Returns:
        Liste von Dictionaries mit Fork-Daten
    """
    try:
        response = requests.get("https://api.llama.fi/protocols", timeout=10)
        response.raise_for_status()
        
        valid_forks = []
        for protocol in response.json():
            try:
                # Safely extract and validate values
                tvl = float(protocol.get('tvl', 0)) if protocol.get('tvl') is not None else 0
                name = str(protocol.get('name', '')).lower()
                
                if tvl > min_tvl and 'uni' in name:
                    valid_forks.append({
                        'name': protocol.get('name', 'Unbekannt'),
                        'tvl': tvl,
                        'chain': protocol.get('chain', 'Unbekannt')
                    })
            except (TypeError, ValueError) as e:
                continue
                
        return valid_forks
        
    except requests.exceptions.RequestException as e:
        print(f"API-Anfrage fehlgeschlagen: {e}")
        return []
    except Exception as e:
        print(f"Unerwarteter Fehler: {str(e)}")
        return []

if __name__ == "__main__":
    print("Testaufruf - Deutsche Version:")
    forks = get_recent_forks()
    print(f"Gefundene Forks: {len(forks)}")