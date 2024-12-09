import pytest
from unittest.mock import patch, MagicMock
from src.services.health import HealthChecker


@pytest.mark.asyncio
async def test_health_check_all_healthy():
    mock_response = MagicMock()
    mock_response.content = "test response"

    with patch("src.services.health.PrometheusConnect") as mock_prom, patch(
        "src.services.health.QdrantClient"
    ) as mock_qdrant, patch(
        "src.services.health.settings"
    ) as mock_settings:

        # Setup mocks
        mock_prom.return_value.check_prometheus_connection = lambda: None
        mock_qdrant.return_value.get_collections = lambda: []

        # Setup synchronous mock for Claude
        mock_client = MagicMock()  # Changed from AsyncMock to MagicMock
        mock_client.messages.create.return_value = mock_response

        # Set provider to CLAUDE
        mock_settings.llm_provider = "claude"

        result = await HealthChecker.check_all()

        assert result["status"] == "healthy"
        assert all(
            service["status"] == "healthy" for service in result["services"].values()
        )


@pytest.mark.asyncio
async def test_health_check_prometheus_unhealthy():
    with patch("src.services.health.PrometheusConnect") as mock_prom:
        mock_prom.return_value.check_prometheus_connection.side_effect = Exception(
            "Connection failed"
        )

        result = await HealthChecker.check_prometheus()
        assert result["status"] == "unhealthy"
        assert "Connection failed" in result["error"]
