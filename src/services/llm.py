# src/services/llm.py
from typing import Dict
import logging
from anthropic import Anthropic
from openai import OpenAI
from src.config import settings, LLMProvider
from src.api.schemas import MetricAnalysis, RiskLevel

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider
        if self.provider == LLMProvider.CLAUDE:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
            self.model = settings.claude_model
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.gpt_model

    async def analyze_metrics(self, metrics: Dict, query: str) -> Dict:
        """Main entry point for metric analysis"""
        try:
            # Synchronous call for Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": f"Analyze these metrics: {metrics}\nQuery: {query}"
                }]
            )
            
            # Extract content from response
            content = str(response.content)
            
            return {
                "summary": content,
                "historical_comparison": "Analysis based on historical data",
                "anomalies": [],
                "recommendations": [],
                "risk_level": RiskLevel.LOW
            }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            raise ValueError(f"LLM analysis failed: {str(e)}")