# tests/unit/test_schemas.py
import pytest
from src.api.schemas import QueryRequest, MetricAnalysis, AnalysisResponse
from pydantic import ValidationError


def test_query_request_empty():
    with pytest.raises(ValidationError):
        QueryRequest(query="")  # Empty string should fail validation


def test_query_request_none():
    with pytest.raises(ValidationError):
        QueryRequest(query=None)  # None should fail validation

def test_analysis_response_valid():
    response = AnalysisResponse(
        current_metrics={"cpu": {"value": 0.8, "timestamp": 1234567890}},
        similar_patterns={"cpu": {"value": 0.7, "timestamp": 1234567890}},
        analysis=MetricAnalysis(
            result="Normal operation",
        ),
    )
    assert "cpu" in response.current_metrics
    assert "cpu" in response.similar_patterns
    assert response.current_metrics["cpu"]["value"] == 0.8
    assert response.similar_patterns["cpu"]["value"] == 0.7
