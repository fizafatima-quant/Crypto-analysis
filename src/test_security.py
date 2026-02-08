# test_security.py
from backtester import DEXBacktester
from security_auditor import SecurityAuditor

# Initialize DEXBacktester
dex = DEXBacktester()

# Give the user sufficient balances
dex.user_balances['alice'] = {'ETH': 100, 'USDC': 50000}

# Add some swaps to trigger MEV
try:
    dex.safe_swap('alice', 'ETH', 'USDC', 50)
except:
    pass
try:
    dex.safe_swap('alice', 'ETH', 'USDC', 30)
except:
    pass

# Run security audit
auditor = SecurityAuditor(dex)
results = auditor.run_audit()

# Print results
print("=== Security Audit Results ===")
for check, status in results.items():
    print(f"{check}: {status}")
