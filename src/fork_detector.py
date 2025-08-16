# fork_detector.py
import requests

def get_recent_forks(min_tvl: float = 1_000_000) -> list:
    """Fetch forks with >$1M TVL from DeFiLlama's protocols list."""
    try:
        response = requests.get("https://api.llama.fi/protocols")
        protocols = response.json()
        
        forks = [
            p for p in protocols 
            if isinstance(p, dict)
            and isinstance(p.get("tvl"), (int, float))  # Check if TVL is a number
            and p["tvl"] > min_tvl
            and "uni" in p.get("name", "").lower()
        ]
        return forks
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    forks = get_recent_forks()
    print(f"Found {len(forks)} forks with TVL > $1M:")
    for fork in forks:
        print(f"- {fork['name']} (TVL: ${fork['tvl']:,.2f})")