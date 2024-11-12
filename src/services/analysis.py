# src/services/analysis.py
from typing import List, Dict
from datetime import datetime
from src.data.prometheus_client import PrometheusClient
from src.data.vector_store import MetricsVectorStore

class MetricsAnalyzer:
    def __init__(self, prometheus_url: str):
        self.prometheus = PrometheusClient(prometheus_url)
        self.vector_store = MetricsVectorStore()
        
    def analyze_query(self, query: str) -> Dict:
        # Get recent metrics
        metrics = self.prometheus.get_node_metrics()
        
        # Store in vector database
        self.vector_store.add_metrics(metrics)
        
        # Get similar historical patterns
        similar_metrics = self.vector_store.similar_metrics(query)
        
        return {
            "current_metrics": metrics,
            "similar_patterns": similar_metrics,
            "analysis": self._generate_analysis(metrics, similar_metrics)
        }
    
    def _generate_analysis(self, current: List[Dict], historical: List[Dict]) -> Dict:
        # Basic analysis comparing current vs historical patterns
        return {
            "summary": "Infrastructure analysis based on metrics",
            "anomalies": self._detect_anomalies(current, historical),
            "recommendations": self._generate_recommendations(current)
        }
    
    def _detect_anomalies(self, current: List[Dict], historical: List[Dict]) -> List[str]:
        anomalies = []
        # Basic threshold-based anomaly detection
        for metric in current:
            if metric['metric'] == 'cpu_usage' and float(metric['value']) > 0.8:
                anomalies.append(f"High CPU usage detected: {metric['value']}")
            elif metric['metric'] == 'memory_usage' and float(metric['value']) > 0.9:
                anomalies.append(f"High memory usage detected: {metric['value']}")
        return anomalies
    
    def _generate_recommendations(self, metrics: List[Dict]) -> List[str]:
        recommendations = []
        for metric in metrics:
            if metric['metric'] == 'cpu_usage' and float(metric['value']) > 0.8:
                recommendations.append("Consider scaling up CPU resources")
            elif metric['metric'] == 'memory_usage' and float(metric['value']) > 0.9:
                recommendations.append("Consider increasing memory allocation")
        return recommendations