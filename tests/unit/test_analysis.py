# tests/unit/test_analysis.py
import pytest
import asyncio
from unittest.mock import patch, MagicMock
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

@pytest.mark.asyncio
async def test_analyze_query():
    # Setup
    mock_metrics = [
        {'metric': 'cpu_usage', 'value': '0.9', 'timestamp': 1234567890}
    ]
    
    mock_prometheus = MagicMock()
    mock_prometheus.get_node_metrics.return_value = mock_metrics
    
    mock_vector_store = MagicMock()
    mock_vector_store.similar_metrics.return_value = mock_metrics
    
    mock_llm = MagicMock()
    future = asyncio.Future()
    future.set_result("Analysis result")
    mock_llm.analyze_metrics.return_value = future
    
    # Initialize analyzer with mocks
    analyzer = MetricsAnalyzer("http://test")
    analyzer.prometheus = mock_prometheus
    analyzer.vector_store = mock_vector_store
    analyzer.llm = mock_llm
    
    # Execute
    result = await analyzer.analyze_query("high cpu usage")
    
    # Assert
    assert "current_metrics" in result
    assert "similar_patterns" in result
    assert "analysis" in result
    mock_prometheus.get_node_metrics.assert_called_once()
    mock_vector_store.similar_metrics.assert_called_once()
    mock_llm.analyze_metrics.assert_called_once()