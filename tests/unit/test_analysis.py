# tests/unit/test_analysis.py
import pytest
from unittest.mock import patch, MagicMock
from src.services.analysis import MetricsAnalyzer


@pytest.fixture
def mock_prometheus():
    with patch("src.data.prometheus_client.PrometheusConnect") as mock:
        client = MagicMock()
        # Mock the connection check
        client.check_prometheus_connection = MagicMock(return_value=True)
        mock.return_value = client
        yield mock


@pytest.fixture
def mock_vector_store():
    with patch("src.data.vector_store.MetricsVectorStore") as mock:
        yield mock


@pytest.fixture
def mock_llm():
    with patch("src.services.llm.LLMService") as mock:
        yield mock


@pytest.fixture
def sample_metrics():
    return [
        {
            "metric": "cpu_usage",
            "data": [
                {
                    "metric": {"instance": "localhost:9100"},
                    "values": [[1234567890, "0.9"]],
                }
            ],
        }
    ]


def test_format_metrics(sample_metrics):
    analyzer = MetricsAnalyzer("http://test")
    result = analyzer._format_metrics(sample_metrics)

    assert len(result) == 1
    assert result[0]["metric"] == "cpu_usage"
    assert result[0]["value"] == 0.9
    assert result[0]["timestamp"] == 1234567890


def test_format_metrics_empty():
    analyzer = MetricsAnalyzer("http://test")
    with pytest.raises(ValueError, match="No valid metrics after formatting"):
        analyzer._format_metrics([])


def test_format_metrics_invalid():
    analyzer = MetricsAnalyzer("http://test")
    with pytest.raises(ValueError, match="No valid metrics after formatting"):
        analyzer._format_metrics([{"invalid": "data"}])


@pytest.mark.asyncio
async def test_analyze_query():
    # Setup mock Prometheus response
    mock_query_response = [
        {"metric": {"__name__": "cpu_usage"}, "values": [[1234567890, "0.9"]]}
    ]

    with patch(
        "src.data.prometheus_client.PrometheusConnect"
    ) as mock_prometheus, patch(
        "src.data.vector_store.MetricsVectorStore"
    ) as mock_vector_store, patch(
        "src.services.llm.LLMService"
    ) as mock_llm:

        # Setup Prometheus mock with proper response structure
        prometheus_client = MagicMock()
        prometheus_client.custom_query_range.return_value = mock_query_response
        mock_prometheus.return_value = prometheus_client

        # Setup VectorStore mock
        vector_store = MagicMock()
        vector_store.similar_metrics.return_value = [
            {"metric": "cpu_usage", "value": 0.8, "timestamp": 1234567890}
        ]
        mock_vector_store.return_value = vector_store

        # Setup LLM mock
        llm = MagicMock()
        llm.analyze_metrics.return_value = {
            "result": "Test analysis",
        }
        mock_llm.return_value = llm

        # Initialize analyzer and execute
        analyzer = MetricsAnalyzer("http://test")
        result = await analyzer.analyze_query("analyze cpu")

        # Assertions
        assert "current_metrics" in result
        assert "similar_patterns" in result
        assert "analysis" in result
        prometheus_client.custom_query_range.assert_called()


@pytest.mark.asyncio
async def test_analyze_query_no_metrics(mock_prometheus):
    with patch("src.data.vector_store.MetricsVectorStore"), patch(
        "src.services.llm.LLMService"
    ):

        # Setup empty metrics response
        mock_prometheus.return_value.get_node_metrics = MagicMock(return_value=[])

        analyzer = MetricsAnalyzer("http://test")

        with pytest.raises(ValueError, match="No valid metrics after formatting"):
            await analyzer.analyze_query("analyze cpu")
