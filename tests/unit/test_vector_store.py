# tests/unit/test_vector_store.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.data.vector_store import MetricsVectorStore


@pytest.fixture
def mock_qdrant():
    with patch("src.data.vector_store.QdrantClient") as mock:
        yield mock


@pytest.fixture
def mock_embeddings():
    with patch("src.data.vector_store.HuggingFaceEmbeddings") as mock:
        embedder = MagicMock()
        embedder.embed_documents.return_value = [[0.1] * 384]  # Match embedding size
        embedder.embed_query.return_value = [0.1] * 384
        mock.return_value = embedder
        yield mock


@pytest.fixture
def test_metrics():
    return [
        {
            "metric": "cpu_usage",
            "value": 0.75,
            "timestamp": int(datetime.now().timestamp()),
        }
    ]


def test_initialization(mock_qdrant):
    mock_client = mock_qdrant.return_value
    mock_client.collection_exists.return_value = False

    mock_client.collection_exists.assert_called_once()
    mock_client.create_collection.assert_called_once()


def test_add_metrics(mock_qdrant, test_metrics):
    store = MetricsVectorStore()
    store.add_metrics(test_metrics)

    # Verify embedding creation
    store.embeddings.embed_documents.assert_called_once()

    # Verify points insertion
    mock_qdrant.return_value.upsert.assert_called_once()

    # Verify payload structure
    call_args = mock_qdrant.return_value.upsert.call_args[1]
    points = call_args["points"]
    assert len(points) == 1
    assert points[0].payload["metric_name"] == "cpu_usage"
    assert points[0].payload["value"] == 0.75
    assert "timestamp" in points[0].payload


def test_similar_metrics(mock_qdrant):
    store = MetricsVectorStore()
    query = "high cpu usage"

    # Mock search results
    mock_result = MagicMock()
    mock_result.payload = {
        "text": "Metric: cpu_usage Value: 0.9",
        "timestamp": int(datetime.now().timestamp()),
        "metric_name": "cpu_usage",
        "value": 0.9,
    }
    mock_qdrant.return_value.search.return_value = [mock_result]

    results = store.similar_metrics(query)

    # Verify search was called
    store.embeddings.embed_query.assert_called_once_with(query)
    mock_qdrant.return_value.search.assert_called_once()

    # Verify results structure
    assert len(results) == 1
    assert "metric_name" in results[0]
    assert "value" in results[0]
    assert "timestamp" in results[0]
