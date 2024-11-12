# src/api/schemas.py
from pydantic import BaseModel, Field, constr
from typing import List, Dict
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class QueryRequest(BaseModel):
    query: constr(min_length=1) = Field(
        ..., 
        description="Query string for analysis"
    )

class MetricAnalysis(BaseModel):
    summary: str = Field(..., description="Overall analysis summary")
    historical_comparison: str = Field(..., description="Comparison with past patterns")
    anomalies: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)

class AnalysisResponse(BaseModel):
    current_metrics: Dict[str, Dict] = Field(..., description="Current metric values")
    similar_patterns: Dict[str, Dict] = Field(..., description="Similar historical patterns")
    analysis: MetricAnalysis = Field(..., description="Analysis results")

class HealthStatus(BaseModel):
    status: str
    error: str | None = None

class HealthCheckResponse(BaseModel):
    status: str
    services: Dict[str, HealthStatus]