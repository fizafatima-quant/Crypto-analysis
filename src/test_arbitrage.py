 
from arbitrage_detector import ArbitrageDetector

class DummyPool:
    def __init__(self, eth, usdc):
        self.reserves = {'ETH': eth, 'USDC': usdc}

def test_arbitrage():
    detector = ArbitrageDetector()
    pool1 = DummyPool(10, 20000)
    pool2 = DummyPool(10, 21000)
    
    detector.add_pool("Pool1", pool1)
    detector.add_pool("Pool2", pool2)
    
    opportunities = detector.find_arbitrage_opportunities()
    print(opportunities)

if __name__ == "__main__":
    test_arbitrage()
