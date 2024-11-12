# src/data/vector_store.py
from typing import List, Dict
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_community.embeddings import HuggingFaceEmbeddings

class MetricsVectorStore:
    def __init__(self, collection_name: str = "metrics"):
        self.collection_name = collection_name
        self.client = QdrantClient(":memory:")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self._create_collection()

    def _create_collection(self):
        """Initialize vector collection"""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE
                )
            )

    def _format_metric_text(self, metric: Dict) -> str:
        return f"Metric: {metric['metric']} Value: {metric['value']} Time: {datetime.fromtimestamp(metric['timestamp'])}"

    def add_metrics(self, metrics: List[Dict]):
        texts = [self._format_metric_text(metric) for metric in metrics]
        embeddings = self.embeddings.embed_documents(texts)
        
        points = [
            models.PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "text": text,
                    "timestamp": metrics[i]['timestamp'],
                    "metric_name": metrics[i]['metric'],
                    "value": metrics[i]['value']
                }
            )
            for i, (text, embedding) in enumerate(zip(texts, embeddings))
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def similar_metrics(self, query: str, k: int = 5) -> List[Dict]:
        query_vector = self.embeddings.embed_query(query)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=k
        )
        
        return [point.payload for point in results]