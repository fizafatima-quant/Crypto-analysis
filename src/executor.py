import os
import time
import logging

class Executor:
    """
    Handles order execution in either paper mode or live mode.
    """
    def __init__(self, exchange=None, mode=None):
        self.mode = mode or os.environ.get("TRADE_MODE", "paper")
        self.exchange = exchange

    def place_order(self, symbol, side, amount, price=None):
        logging.info(f"[{self.mode}] {side} {amount} {symbol} @ {price or 'market'}")
        
        if self.mode == "paper":
            # Simulate order execution
            time.sleep(0.05)
            return {
                "id": f"paper-{int(time.time()*1000)}",
                "status": "filled",
                "symbol": symbol,
                "side": side,
                "amount": amount,
                "price": price
            }
        
        # Live mode
        try:
            return self.exchange.create_order(symbol, 'limit' if price else 'market', side, amount, price)
        except Exception as e:
            logging.exception("Live order failed")
            raise
