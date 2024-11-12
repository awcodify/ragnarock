# src/data/prometheus_client.py
from typing import List, Dict
from datetime import datetime, timedelta
from prometheus_api_client import PrometheusConnect

class PrometheusClient:
    def __init__(self, url: str):
        self.client = PrometheusConnect(url=url, disable_ssl=True)
        
    def get_node_metrics(self, time_range: int = 3600) -> List[Dict]:
        """
        Fetch basic infrastructure metrics
        Args:
            time_range: Time range in seconds (default 1h)
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=time_range)
        
        metrics = {
            'cpu_usage': 'sum(rate(node_cpu_seconds_total{mode="user", instance=~".*swarm.*"}[5m])) by (instance)',
            'memory_usage': 'sum by(instance) (node_memory_MemTotal_bytes{instance=~".*swarm.*"}) - sum by(instance)  (node_memory_MemAvailable_bytes{instance=~".*swarm.*"})',
            'disk_usage': 'node_filesystem_size_bytes - node_filesystem_free_bytes',
            'network_receive': 'rate(node_network_receive_bytes_total[5m])',
            'network_transmit': 'rate(node_network_transmit_bytes_total[5m])'
        }
        
        results = []
        for metric_name, query in metrics.items():
            metric_data = self.client.custom_query_range(
                query=query,
                start_time=start_time,
                end_time=end_time,
                step='5m'
            )
            results.append({
                'metric': metric_name,
                'data': metric_data
            })
            
        return results