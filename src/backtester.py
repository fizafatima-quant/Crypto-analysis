import numpy as np 
# DEX Backtester - Complete Implementation
class DEXSimulator:
    def __init__(self):
        """Initialize with ETH/USDC and WBTC/USDC pools"""
        self.POOL_RESERVES = {
            # Format: {input_token: {output_token: (input_reserve, output_reserve)}}
            'ETH': {
                'USDC': (1000.0, 2_000_000.0),  # 1000 ETH : 2M USDC
                'WBTC': (1000.0, 50.0)           # 1000 ETH : 50 WBTC
            },
            'USDC': {
                'ETH': (2_000_000.0, 1000.0),
                'WBTC': (2_000_000.0, 50.0)
            },
            'WBTC': {
                'ETH': (50.0, 1000.0),
                'USDC': (50.0, 2_000_000.0)
            }
        }

    def calculate_output(self, amount_in, reserve_in, reserve_out):
        """Uniswap V2 AMM formula with 0.3% fee"""
        amount_in_with_fee = amount_in * 0.997  # 0.3% LP fee
        return (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)

    def simulate_trade(self, amount_in, token_in, token_out):
        """Execute trade and update pool reserves"""
        reserve_in, reserve_out = self.POOL_RESERVES[token_in][token_out]
        amount_out = self.calculate_output(amount_in, reserve_in, reserve_out)
        
        # Update pool state
        self.POOL_RESERVES[token_in][token_out] = (reserve_in + amount_in, reserve_out - amount_out)
        self.POOL_RESERVES[token_out][token_in] = (reserve_out - amount_out, reserve_in + amount_in)
        
        return amount_out

    def print_pool_state(self):
        """Display current pool reserves"""
        print("\nCurrent Pool Reserves:")
        for token, pairs in self.POOL_RESERVES.items():
            print(f"{token}:")
            for pair, reserves in pairs.items():
                print(f"  → {pair}: {reserves[0]:,.2f} {token} / {reserves[1]:,.2f} {pair}")

def main():
    dex = DEXSimulator()
    
    # Initial state
    print("=== DEX Simulation Started ===")
    dex.print_pool_state()
    
    # Test Case 1: Small ETH→USDC swap
    eth_amount = 1.0
    usdc_received = dex.simulate_trade(eth_amount, "ETH", "USDC")
    print(f"\nTest 1: Swap {eth_amount} ETH → {usdc_received:,.2f} USDC")
    dex.print_pool_state()
    
    # Test Case 2: Large ETH→USDC swap (show slippage)
    eth_amount = 100.0
    usdc_received = dex.simulate_trade(eth_amount, "ETH", "USDC")
    print(f"\nTest 2: Swap {eth_amount} ETH → {usdc_received:,.2f} USDC")
    dex.print_pool_state()
    
    # Test Case 3: USDC→WBTC swap
    usdc_amount = 50000.0
    wbtc_received = dex.simulate_trade(usdc_amount, "USDC", "WBTC")
    print(f"\nTest 3: Swap {usdc_amount:,.2f} USDC → {wbtc_received:.6f} WBTC")
    dex.print_pool_state()

if __name__ == "__main__":
    main()