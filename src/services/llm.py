# src/services/llm.py
from typing import Dict
import logging
from tensorzero import TensorZeroGateway
from src.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.llm_gateway_url = settings.llm_gateway_url

    async def analyze_metrics(self, metrics: Dict, query: str) -> Dict:
        """Main entry point for metric analysis"""
        try:
            with TensorZeroGateway(self.llm_gateway_url) as client:
                response = client.inference(
                    function_name="generate_analysis",
                    input={
                        "messages": [
                            {
                                "role": "user",
                                "content": {"metrics": metrics, "query": query},
                            }
                        ]
                    }
                )

                print(response.content)

                return {
                    "result": response.content[0].text
                }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            raise ValueError(f"LLM analysis failed: {str(e)}")
