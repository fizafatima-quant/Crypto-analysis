import pytest
from monitoring import MonitoringSystem

def test_monitoring_alerts():
    system = MonitoringSystem()
    
    # Case 1: High MEV activity triggers alert
    alerts = system.check_alerts({'high_mev_activity': 0.5})
    assert 'high_mev_activity' in alerts
    
    # Case 2: Liquidity crisis triggers alert
    alerts = system.check_alerts({'liquidity_crisis': {'ETH': 500, 'USDC': 2000}})
    assert 'liquidity_crisis' in alerts
    
    # Case 3: Performance degradation triggers alert
    alerts = system.check_alerts({'performance_degradation': 3})
    assert 'performance_degradation' in alerts
    
    # Case 4: No alert
    alerts = system.check_alerts({'high_mev_activity': 0.1, 'performance_degradation': 10, 'liquidity_crisis': {'ETH': 2000}})
    assert alerts == []
