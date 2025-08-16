# src/alert.py
def log_fork(fork: dict):
    """Basic console alerts without Telegram"""
    try:
        tvl = fork.get('tvl', 0)
        print(f"New fork detected: {fork.get('name', 'Unknown')} (TVL: ${tvl/1e6:.2f}M)")
    except Exception as e:
        print(f"Alert error: {e}")