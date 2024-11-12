# src/api/main.py
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from src.services.analysis import MetricsAnalyzer
from src.config import settings

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Infrastructure RAG API")

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/analyze")
async def analyze_metrics(request: QueryRequest) -> Dict:
    try:
        analyzer = MetricsAnalyzer(settings.prometheus_url)
        results = await analyzer.analyze_query(request.query)  # Make async call
        logger.info(f"Successfully analyzed query: {request.query}")
        return results
    except Exception as e:
        logger.error(f"Error analyzing metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_raw_metrics() -> List[Dict]:
    try:
        analyzer = MetricsAnalyzer(settings.prometheus_url)
        metrics = analyzer.prometheus.get_node_metrics()
        logger.info("Successfully retrieved raw metrics")
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        if "Connection refused" in str(e):
            raise HTTPException(
                status_code=503,
                detail="Prometheus connection failed"
            )
        raise HTTPException(status_code=500, detail=str(e))