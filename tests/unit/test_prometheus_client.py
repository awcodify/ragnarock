# tests/unit/test_prometheus_client.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.data.prometheus_client import PrometheusClient


@pytest.fixture
def mock_prometheus():
    with patch("src.data.prometheus_client.PrometheusConnect") as mock:
        yield mock


def test_get_node_metrics(mock_prometheus):
    client = PrometheusClient("http://localhost:9090")
    mock_prometheus.return_value.custom_query_range.return_value = [
        {"metric": {"instance": "node1"}, "values": [[1234567890, "0.5"]]}
    ]

    results = client.get_node_metrics(time_range=3600)

    assert len(results) == 5  # 5 metrics
    assert all("metric" in result for result in results)
    assert all("data" in result for result in results)
