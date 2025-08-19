Crypto DEX MEV Analysis

🛡️ Project Overview



This project simulates MEV detection and prevention on a simplified decentralized exchange (DEX).



Features:



Detects potential sandwich attacks and MEV trades



Blocks trades that could cause extreme price manipulation



Demonstrates local attack simulations



Optimized for gas efficiency



📂 File Descriptions

File	Purpose

mev\_resistance.py	MEV detection logic (is\_sandwich\_safe) with imbalance ratio and trade impact checks

dex\_backtester.py	AMM pool simulation and swap execution with gas optimizations

mev\_attacker.py	Demonstrates normal trades and blocked MEV attacks

test\_dex\_backtester.py	Unit tests for large trades and MEV blocking scenarios

⚡ Key Features



Enhanced MEV Detection



Blocks trades in highly imbalanced pools (ratio > 20)



Prevents large trades that could manipulate prices



Local Attack Simulation



Demonstrates normal trades succeed



Blocks MEV-style large trades



Shows detection on imbalanced pools



Gas Optimizations



Cached reserve lookups in swap() method



Reduces unnecessary dictionary reads (~200 gas saved per swap)



Testing



Confirms MEV attacks are blocked



Ensures normal trades are unaffected

