import requests
from typing import Dict, Any

class ForkDetector:
    def __init__(self):
        self.oracle_urls = {
            'defillama': 'https://api.llama.fi/pools',
            'chainlink': 'https://data.chain.link/v1/feeds'  # Mock endpoint
        }
        self.timeout = 5  # seconds
    
    def get_pool_metadata(self, pool_address: str) -> Dict[str, Any]:
        """Fetch pool metadata with error handling"""
        try:
            # Try DeFiLlama first
            response = requests.get(
                f"{self.oracle_urls['defillama']}/{pool_address}",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            
            # Fallback response
            return {
                'description': 'mainnet uniswap v2 pool',
                'tokens': ['ETH', 'USDC']
            }
        except (requests.RequestException, requests.Timeout):
            return {'description': '', 'tokens': []}

    def detect_fork(self, target_pool: str) -> bool:
        """
        Detect if a pool is from a forked network
        Returns:
            bool: True if fork detected, False otherwise
        """
        metadata = self.get_pool_metadata(target_pool)
        description = metadata.get('description', '').lower()
        
        fork_keywords = {'fork', 'copy', 'clone', 'testnet', 'mock'}
        return any(keyword in description for keyword in fork_keywords)

# Test with mock data
if __name__ == "__main__":
    print("=== Testing Fork Detector ===")
    
    detector = ForkDetector()
    
    # Mock test cases
    test_pools = {
        "legit_pool": "0xb4e16d0168e52d35cacd2c6185b44281ec28c9dc",  # Real ETH-USDC
        "fork_pool": "0x123abc",  # Simulated fork
        "invalid_pool": "0xinvalid"  # Should fail gracefully
    }
    
    for name, address in test_pools.items():
        is_fork = detector.detect_fork(address)
        print(f"{name.upper():<12} | Fork: {is_fork}")