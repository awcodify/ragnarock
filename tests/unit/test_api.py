# tests/unit/test_api.py
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('src.services.analysis.PrometheusClient')
@patch('src.services.analysis.MetricsVectorStore')
def test_analyze_metrics(mock_vector_store, mock_prometheus):
    # Setup mock responses
    mock_prometheus.return_value.get_node_metrics.return_value = [
        {'metric': 'cpu_usage', 'value': '0.9', 'timestamp': 1234567890}
    ]
    
    mock_vector_store.return_value.similar_metrics.return_value = [
        {'metric': 'cpu_usage', 'value': '0.85', 'timestamp': 1234567880}
    ]

    # Make request
    response = client.post(
        "/analyze",
        json={"query": "high cpu usage"}
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "current_metrics" in data
    assert "similar_patterns" in data
    assert "analysis" in data
    assert isinstance(data["analysis"], dict)
    assert "recommendations" in data["analysis"]

    # Verify mocks were called
    mock_prometheus.return_value.get_node_metrics.assert_called_once()
    mock_vector_store.return_value.similar_metrics.assert_called_once()

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