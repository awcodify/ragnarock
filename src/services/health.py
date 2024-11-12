from typing import Dict
from prometheus_api_client import PrometheusConnect
from qdrant_client import QdrantClient
from anthropic import Anthropic
from openai import OpenAI
from src.config import settings, LLMProvider
import logging

logger = logging.getLogger(__name__)

class HealthChecker:
    @staticmethod
    async def check_prometheus() -> Dict:
        try:
            client = PrometheusConnect(url=settings.prometheus_url, disable_ssl=True)
            client.check_prometheus_connection()
            return {"status": "healthy"}
        except Exception as e:
            logger.error(f"Prometheus health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_vector_store() -> Dict:
        try:
            client = QdrantClient(":memory:")
            client.get_collections()
            return {"status": "healthy"}
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_llm() -> Dict:
        try:
            if settings.llm_provider == LLMProvider.CLAUDE:
                client = Anthropic(api_key=settings.anthropic_api_key)
                # Use synchronous call for Claude
                response = client.messages.create(
                    model=settings.claude_model,
                    max_tokens=1,
                    messages=[{"role": "user", "content": "hi"}]
                )
                if not response:
                    raise Exception("No response from Claude")
            else:
                client = OpenAI(api_key=settings.openai_api_key)
                response = await client.chat.completions.create(
                    model=settings.gpt_model,
                    max_tokens=1,
                    messages=[{"role": "user", "content": "hi"}]
                )
            return {"status": "healthy"}
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}

    @staticmethod
    async def check_all() -> Dict:
        results = {
            "prometheus": await HealthChecker.check_prometheus(),
            "vector_store": await HealthChecker.check_vector_store(),
            "llm": await HealthChecker.check_llm(),
        }
        
        overall_status = "healthy" if all(
            service["status"] == "healthy" for service in results.values()
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "services": results
        }