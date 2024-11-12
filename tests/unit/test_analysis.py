# tests/unit/test_analysis.py
import pytest
from unittest.mock import Mock, patch
from src.services.analysis import MetricsAnalyzer

@pytest.fixture
def mock_prometheus():
    with patch('src.services.analysis.PrometheusClient') as mock:
        client = Mock()
        client.get_node_metrics.return_value = [
            {'metric': 'cpu_usage', 'value': '0.9', 'timestamp': 1234567890}
        ]
        mock.return_value = client
        yield mock

@pytest.fixture
def mock_vector_store():
    with patch('src.services.analysis.MetricsVectorStore') as mock:
        store = Mock()
        store.similar_metrics.return_value = [
            {'metric': 'cpu_usage', 'value': '0.85', 'timestamp': 1234567880}
        ]
        mock.return_value = store
        yield mock

def test_analyze_query(mock_prometheus, mock_vector_store):
    analyzer = MetricsAnalyzer("http://localhost:9090")
    result = analyzer.analyze_query("high cpu usage")
    
    assert "current_metrics" in result
    assert "similar_patterns" in result
    assert "analysis" in result
    assert len(result["analysis"]["anomalies"]) > 0
    assert len(result["analysis"]["recommendations"]) > 0