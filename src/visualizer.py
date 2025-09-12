import matplotlib.pyplot as plt

class PerformanceVisualizer:
    def __init__(self, backtester):
        self.backtester = backtester

    def create_dashboard(self):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # Success rate over time
        success_rates = []
        swaps = self.backtester.swap_history
        for i in range(1, len(swaps)+1):
            recent = swaps[:i]
            success_rate = sum(1 for s in recent if s['status']=="success") / i
            success_rates.append(success_rate)
        ax1.plot(success_rates)
        ax1.set_title("Success Rate Over Time")
        ax1.set_ylabel("Success Rate")

        # Slippage distribution
        impacts = [s['price_impact'] for s in swaps if s['status']=="success"]
        ax2.hist(impacts, bins=10)
        ax2.set_title("Price Impact Distribution")

        # Trade outcomes pie
        report = self.backtester.monitor.get_report()
        sizes = [report['success_rate'], report['mev_block_rate'], report['slippage_revert_rate']]
        if sum(sizes)==0: sizes=[1,0,0]  # avoid NaN
        labels = ["Successful", "MEV Blocked", "Slippage Reverted"]
        ax3.pie(sizes, labels=labels, autopct="%1.1f%%")
        ax3.set_title("Trade Outcomes")

        # Volume over time
        volumes = [s['amount_in'] for s in swaps]
        ax4.plot(volumes)
        ax4.set_title("Trade Volume Over Time")

        plt.tight_layout()
        plt.savefig("performance_dashboard.png")
        plt.close()
