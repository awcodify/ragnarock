# tests/unit/test_schemas.py
import pytest
from src.api.schemas import QueryRequest, MetricAnalysis, AnalysisResponse, RiskLevel
from pydantic import ValidationError

def test_query_request_empty():
    with pytest.raises(ValidationError):
        QueryRequest(query="")  # Empty string should fail validation

def test_query_request_none():
    with pytest.raises(ValidationError):
        QueryRequest(query=None)  # None should fail validation

def test_analysis_response_valid():
    response = AnalysisResponse(
        current_metrics={"cpu": 0.8},
        similar_patterns={"cpu": 0.7},
        analysis=MetricAnalysis(
            summary="Normal operation",
            historical_comparison="Stable",
            anomalies=[],
            recommendations=[],
            risk_level=RiskLevel.LOW
        )
    )
    assert isinstance(response.analysis, MetricAnalysis)

def test_metric_analysis_invalid_risk():
    with pytest.raises(ValidationError):
        MetricAnalysis(
            summary="test",
            historical_comparison="test",
            risk_level="INVALID"
        )

# tests/unit/test_schemas.py
def test_analysis_response_valid():
    response = AnalysisResponse(
        current_metrics={
            "cpu": {
                "value": 0.8,
                "timestamp": 1234567890
            }
        },
        similar_patterns={
            "cpu": {
                "value": 0.7,
                "timestamp": 1234567890
            }
        },
        analysis=MetricAnalysis(
            summary="Normal operation",
            historical_comparison="Stable",
            anomalies=[],
            recommendations=[],
            risk_level=RiskLevel.LOW
        )
    )
    assert "cpu" in response.current_metrics
    assert "cpu" in response.similar_patterns
    assert response.analysis.risk_level == RiskLevel.LOW
    assert response.current_metrics["cpu"]["value"] == 0.8
    assert response.similar_patterns["cpu"]["value"] == 0.7