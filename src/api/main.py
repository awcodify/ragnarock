from fastapi import FastAPI, HTTPException
from src.api.schemas import AnalysisResponse, QueryRequest
from src.services.analysis import MetricsAnalyzer
from src.services.health import HealthChecker
from src.api.schemas import HealthCheckResponse
from src.config import settings
import logging
import traceback

logger = logging.getLogger(__name__) 

app = FastAPI(
    title="Infrastructure RAG",
    description="Real-time infrastructure analysis using RAG",
    version="1.0.0",
)

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_metrics(request: QueryRequest) -> AnalysisResponse:
    try:
        logger.info(f"Received analysis request with query: {request.query}")
        analyzer = MetricsAnalyzer(settings.prometheus_url)
        
        logger.debug(f"Connecting to Prometheus at: {settings.prometheus_url}")
        results = await analyzer.analyze_query(request.query)
        
        logger.info("Analysis completed successfully")
        return AnalysisResponse(**results)
        
    except Exception as e:
        logger.error(
            f"Error analyzing metrics for query '{request.query}'\n"
            f"Error type: {type(e).__name__}\n"
            f"Error message: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {type(e).__name__} - {str(e)}"
        )
    
@app.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    try:
        return await HealthChecker.check_all()
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )