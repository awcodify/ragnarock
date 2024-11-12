# src/templates/prompts.py
from string import Template

METRIC_ANALYSIS_TEMPLATE = Template("""
Analyze the following infrastructure metrics:

Current Metrics:
$current_metrics

Historical Similar Patterns:
$historical_metrics

Query: $query

Please provide:
1. Summary of current state
2. Comparison with historical patterns
3. Potential issues or anomalies
4. Recommendations for optimization
5. Risk assessment (Low/Medium/High)

Focus on infrastructure performance and reliability.
""")

class PromptGenerator:
    @staticmethod
    def generate_analysis_prompt(current_metrics: dict, historical_metrics: dict, query: str) -> str:
        return METRIC_ANALYSIS_TEMPLATE.substitute(
            current_metrics=current_metrics,
            historical_metrics=historical_metrics,
            query=query
        )