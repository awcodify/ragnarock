from typing import Dict, List
from datetime import datetime
from src.data.prometheus_client import PrometheusClient
from src.data.vector_store import MetricsVectorStore
from src.services.llm import LLMService
import logging

logger = logging.getLogger(__name__)

class MetricsAnalyzer:
    def __init__(self, prometheus_url: str):
        self.prometheus = PrometheusClient(prometheus_url)
        self.vector_store = MetricsVectorStore()
        self.llm = LLMService()

    def _format_metrics(self, raw_metrics: List[Dict]) -> List[Dict]:
      """Format raw prometheus metrics for vector store"""
      formatted = []
      for metric_group in raw_metrics:
          try:
              metric_name = metric_group['metric']
              metric_data = metric_group['data'][0]  # Get first data group
              
              # Get latest values from the values array
              latest_values = metric_data['values'][-1]  # Get last timestamp-value pair
              timestamp, value = latest_values
              
              formatted.append({
                  'metric': metric_name,
                  'value': float(value),
                  'timestamp': int(float(timestamp))
              })
              logger.debug(f"Formatted metric: {metric_name} = {value} @ {timestamp}")
              
          except (KeyError, IndexError, ValueError) as e:
              logger.warning(
                  f"Error formatting metric group: {metric_group}\n"
                  f"Error: {str(e)}"
              )
              continue
              
      if not formatted:
          logger.error("No metrics could be formatted")
          raise ValueError("No valid metrics after formatting")
          
      return formatted

    async def analyze_query(self, query: str) -> Dict:
      # Get and format metrics
      raw_metrics = self.prometheus.get_node_metrics()
      formatted_metrics = self._format_metrics(raw_metrics)
      
      # Convert list to dictionary
      current_metrics = {
          m['metric']: {
              'value': m['value'],
              'timestamp': m['timestamp']
          } for m in formatted_metrics
      }
      
      # Get similar patterns
      similar = self.vector_store.similar_metrics(query)
      similar_patterns = {
          m['metric_name']: {
              'value': m['value'],
              'timestamp': m['timestamp']
          } for m in similar
      }
      
      # Get LLM analysis
      llm_response = await self.llm.analyze_metrics(
          {"current": current_metrics, "historical": similar_patterns},
          query
      )
      
      # Convert ContentBlock to string if needed
      if hasattr(llm_response['summary'], 'text'):
          llm_response['summary'] = llm_response['summary'].text
      
      return {
          "current_metrics": current_metrics,
          "similar_patterns": similar_patterns,
          "analysis": llm_response
      }