import logging

# Step 1: Set up logging (saves errors to 'mev_errors.log')
logging.basicConfig(
    filename='mev_errors.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Step 2: Add error handling to your MEV check
def is_sandwich_safe(tx_hash):
    try:
        # Imagine this is your MEV detection logic
        if tx_hash == "0xHACK":  # Example: Pretend this is a bad TX
            raise ValueError("Sandwich attack detected!")
        return True
    except Exception as e:
        logging.error(f"🚨 MEV check failed for {tx_hash}: {str(e)}", exc_info=True)
        return False  # Fail-safe: Assume unsafe if error happens

# Step 3: Test it
if __name__ == "__main__":
    # Simulate checking 3 transactions (1 bad, 2 good)
    for tx in ["0xSAFE", "0xHACK", "0xALSO_SAFE"]:
        print(f"Checking TX: {tx}")
        result = is_sandwich_safe(tx)
        print(f"Result: {'✅ Safe' if result else '❌ Unsafe'}\n")