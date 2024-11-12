from datetime import datetime
from typing import Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

# Constants
VECTOR_SIZE = 384  # MiniLM embedding size
METRIC = models.Distance.COSINE

class MetricsVectorStore:
    def __init__(self, collection_name: str = "metrics"):
        self.collection_name = collection_name
        self.client = QdrantClient(":memory:")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self._create_collection()

    def _create_collection(self) -> None:
        """Initialize vector collection"""
        try:
            if not self.client.collection_exists(self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=VECTOR_SIZE,
                        distance=METRIC
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise

    def _format_metric_text(self, metric: Dict) -> Optional[str]:
        try:
            metric_name = metric['metric']
            value = metric['value']
            timestamp = metric['timestamp']
            
            return f"Metric: {metric_name} Value: {value} Time: {datetime.fromtimestamp(timestamp)}"
        except Exception as e:
            logger.error(f"Error formatting metric: {metric}\nError: {str(e)}")
            return None
        
    def add_metrics(self, metrics: List[Dict]) -> None:
      """Add metrics to vector store"""
      try:
          texts = [
              text for text in (self._format_metric_text(metric) for metric in metrics)
              if text is not None
          ]
          
          if not texts:
              logger.error("No valid metrics could be formatted")
              raise ValueError("Failed to format any metrics")

          # Create embeddings
          embeddings = self.embeddings.embed_documents(texts)

          # Create points
          points = [
              models.PointStruct(
                  id=i,
                  vector=embedding,
                  payload={
                      'text': text,
                      'metric_name': metrics[i]['metric'],
                      'value': metrics[i]['value'],
                      'timestamp': metrics[i]['timestamp']
                  }
              )
              for i, (text, embedding) in enumerate(zip(texts, embeddings))
          ]

          # Insert into vector store
          self.client.upsert(
              collection_name=self.collection_name,
              points=points
          )
      except Exception as e:
          logger.error(f"Error adding metrics: {str(e)}")
          raise

    def similar_metrics(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar metrics"""
        try:
            # Get query embedding
            query_vector = self.embeddings.embed_query(query)
            
            # Search similar vectors
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            return [result.payload for result in results]
        except Exception as e:
            logger.error(f"Error searching similar metrics: {str(e)}")
            raise