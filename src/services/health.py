from typing import Dict
from prometheus_api_client import PrometheusConnect
from qdrant_client import QdrantClient
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    @staticmethod
    async def check_prometheus() -> Dict:
        try:
            client = PrometheusConnect(url=settings.prometheus_url, disable_ssl=False)
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
    async def check_all() -> Dict:
        results = {
            "prometheus": await HealthChecker.check_prometheus(),
            "vector_store": await HealthChecker.check_vector_store(),
        }

        overall_status = (
            "healthy"
            if all(service["status"] == "healthy" for service in results.values())
            else "unhealthy"
        )

        return {"status": overall_status, "services": results}
