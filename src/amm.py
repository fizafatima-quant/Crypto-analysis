class AMM:
    def __init__(self, reserves: dict):
        self.reserves = reserves.copy()
    
    def _other_token(self, token_in: str) -> str:
        return [t for t in self.reserves if t != token_in][0]
    
    def execute_swap(self, amount_in: float, token_in: str) -> float:
        token_out = self._other_token(token_in)
        k = self.reserves[token_in] * self.reserves[token_out]
        self.reserves[token_in] += amount_in
        amount_out = self.reserves[token_out] - (k / self.reserves[token_in])
        self.reserves[token_out] = k / self.reserves[token_in]
        return amount_out