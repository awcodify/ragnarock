import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient
import httpx
from fastapi.testclient import TestClient
from src.api.main import app
import asyncio

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_analyze_metrics():
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        mock_metrics = [
            {'metric': 'cpu_usage', 'value': '0.9', 'timestamp': 1234567890}
        ]
        
        mock_analyzer = MagicMock()
        future = asyncio.Future()
        future.set_result({
            "current_metrics": mock_metrics,
            "similar_patterns": mock_metrics,
            "analysis": "Analysis result"
        })
        mock_analyzer.analyze_query.return_value = future
        
        with patch('src.api.main.MetricsAnalyzer', return_value=mock_analyzer):
            response = await ac.post("/analyze", json={"query": "high cpu usage"})
            assert response.status_code == 200

def test_get_raw_metrics():
    # Setup mock data
    mock_metrics = [
        {'metric': 'cpu_usage', 'value': '0.9', 'timestamp': 1234567890}
    ]
    
    # Create nested mock structure
    mock_prometheus = MagicMock()
    mock_prometheus.get_node_metrics.return_value = mock_metrics
    
    mock_analyzer = MagicMock()
    mock_analyzer.prometheus = mock_prometheus
    
    # Patch MetricsAnalyzer constructor
    with patch('src.api.main.MetricsAnalyzer', return_value=mock_analyzer):
        response = client.get("/metrics")
        
        # Assertions
        assert response.status_code == 200
        assert response.json() == mock_metrics
        mock_prometheus.get_node_metrics.assert_called_once()