# tests/unit/test_vector_store.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.data.vector_store import MetricsVectorStore
from qdrant_client.http.exceptions import UnexpectedResponse
# used for mocking the embeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


@pytest.fixture
def mock_qdrant():
    with patch('src.data.vector_store.QdrantClient') as mock:
        client = MagicMock()
        client.collection_exists.return_value = False
        client.create_collection = MagicMock()
        mock.return_value = client
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
    MetricsVectorStore()
    mock_qdrant.return_value.collection_exists.assert_called_once()
    mock_qdrant.return_value.create_collection.assert_called_once()


def test_initialization_failed(mock_qdrant):
    mock_qdrant.return_value.collection_exists.side_effect = UnexpectedResponse(
        status_code=500,
        reason_phrase="Internal Server Error",
        content=b"Error",
        headers={}
    )
    with pytest.raises(Exception):
        MetricsVectorStore()


def test_add_metrics(mock_qdrant, mock_embeddings, test_metrics):
    store = MetricsVectorStore()
    store.add_metrics(test_metrics)
    
    mock_qdrant.return_value.upsert.assert_called_once()
    args = mock_qdrant.return_value.upsert.call_args[1]
    assert 'points' in args
    assert len(args['points']) == 1
    assert args['points'][0].payload['metric_name'] == 'cpu_usage'


def test_similar_metrics(mock_qdrant, mock_embeddings):
    store = MetricsVectorStore()
    mock_qdrant.return_value.search.return_value = [
        MagicMock(payload={
            'metric': 'cpu_usage',
            'value': 0.75,
            'timestamp': 1234567890
        })
    ]
    
    results = store.similar_metrics("high cpu usage")
    
    mock_qdrant.return_value.search.assert_called_once()
    assert len(results) == 1
    assert results[0]['metric'] == 'cpu_usage'


def test_format_metric_invalid():
    store = MetricsVectorStore()
    result = store._format_metric_text({'invalid': 'data'})
    assert result is None


def test_add_metrics_no_valid():
    store = MetricsVectorStore()
    with pytest.raises(ValueError, match="Failed to format any metrics"):
        store.add_metrics([{'invalid': 'data'}])
