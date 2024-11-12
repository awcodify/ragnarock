import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
import httpx
from fastapi.testclient import TestClient
from src.api.main import app
import asyncio
from src.api.schemas import MetricAnalysis, RiskLevel

@pytest.mark.asyncio
async def test_analyze_metrics():
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        # Format metrics as dictionary
        mock_metrics = {
            "cpu_usage": {
                "value": 0.9,
                "timestamp": 1234567890
            }
        }
        
        # Create valid MetricAnalysis instance
        mock_analysis = MetricAnalysis(
            summary="High CPU usage detected",
            historical_comparison="Above normal levels",
            anomalies=["CPU spike detected"],
            recommendations=["Consider scaling up"],
            risk_level=RiskLevel.HIGH
        )

        mock_analyzer = MagicMock()
        future = asyncio.Future()
        future.set_result({
            "current_metrics": mock_metrics,
            "similar_patterns": mock_metrics,
            "analysis": mock_analysis
        })
        mock_analyzer.analyze_query.return_value = future
        
        with patch('src.api.main.MetricsAnalyzer', return_value=mock_analyzer):
            response = await ac.post("/analyze", json={"query": "high cpu usage"})
            assert response.status_code == 200
            data = response.json()
            assert "current_metrics" in data
            assert "analysis" in data
            assert data["analysis"]["risk_level"] == "high"