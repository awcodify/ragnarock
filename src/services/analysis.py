# src/services/analysis.py
from typing import Dict, List
from src.data.prometheus_client import PrometheusClient
from src.data.vector_store import MetricsVectorStore
from src.services.llm import LLMService

class MetricsAnalyzer:
    def __init__(self, prometheus_url: str):
        self.prometheus = PrometheusClient(prometheus_url)
        self.vector_store = MetricsVectorStore()
        self.llm = LLMService()
    
    async def analyze_query(self, query: str) -> Dict:
        # Get current metrics
        metrics = self.prometheus.get_node_metrics()
        
        # Store in vector database for similarity search
        self.vector_store.add_metrics(metrics)
        
        # Get similar historical patterns
        similar_metrics = self.vector_store.similar_metrics(query)
        
        # Generate LLM analysis
        analysis = await self.llm.analyze_metrics(
            {
                "current": metrics,
                "historical": similar_metrics
            },
            query
        )
        
        return {
            "current_metrics": metrics,
            "similar_patterns": similar_metrics,
            "analysis": analysis
        }