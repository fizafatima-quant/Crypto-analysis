from typing import Dict, List, Any

class MonitoringSystem:
    def __init__(self):
        self.metrics = {}
        self.alert_rules = {
            'high_mev_activity': lambda x: isinstance(x, (int, float)) and x > 0.2,
            'liquidity_crisis': lambda reserves: isinstance(reserves, dict) and min(reserves.values()) < 1000,
            'performance_degradation': lambda sps: isinstance(sps, (int, float)) and sps < 5
        }
    
    def check_alerts(self, current_metrics: Dict[str, Any]) -> List[str]:
        """Check all alert conditions"""
        triggered_alerts = []
        for alert_name, condition in self.alert_rules.items():
            if condition(current_metrics.get(alert_name, None)):
                triggered_alerts.append(alert_name)
        return triggered_alerts
