from fastapi import FastAPI, HTTPException
from src.api.schemas import AnalysisResponse, QueryRequest
from src.services.analysis import MetricsAnalyzer  # Add this import
from src.config import settings
import logging

logger = logging.getLogger(__name__) 

app = FastAPI(
    title="Infrastructure RAG",
    description="Real-time infrastructure analysis using RAG",
    version="1.0.0",
)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_metrics(request: QueryRequest) -> AnalysisResponse:
    try:
        analyzer = MetricsAnalyzer(settings.prometheus_url)
        results = await analyzer.analyze_query(request.query)
        return AnalysisResponse(**results)
    except Exception as e:
        logger.error(f"Error analyzing metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))