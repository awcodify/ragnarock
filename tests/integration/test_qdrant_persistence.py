import pytest
from src.data.vector_store import MetricsVectorStore
import time


@pytest.fixture(scope="module")
def qdrant_store():
    # Use test server details
    store = MetricsVectorStore(
        host="localhost",
        port=6333
    )
    return store


@pytest.mark.integration
def test_persistence_across_restarts(qdrant_store):
    # 1. Store test metrics
    test_metrics = [{
        'metric': 'test_cpu',
        'value': 0.75,
        'timestamp': int(time.time())
    }]
    qdrant_store.add_metrics(test_metrics)
    
    # 2. Query to verify storage
    results = qdrant_store.similar_metrics("cpu usage")
    assert len(results) > 0
    
    # 3. Create new connection
    new_store = MetricsVectorStore(
        host="localhost",
        port=6333
    )
    
    # 4. Verify data persists
    new_results = new_store.similar_metrics("cpu usage")
    assert len(new_results) > 0