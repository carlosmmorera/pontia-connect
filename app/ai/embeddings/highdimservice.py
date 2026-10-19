"""
High Dimension Embedding Service module.

This module defines a service based on EmbeddingService for managing
embeddings by using a cloud-based high-dimensional model with Google
Cloud Vertex AI.
"""

__version__ = "1.0"
__author__ = "Carlos Moreno Morera"

from typing import List, Tuple
import numpy as np

from vertexai.language_models import TextEmbeddingModel

from app.ai.embeddings import EmbeddingService


class HighDimEmbeddingService(EmbeddingService):
    """
    Cloud-based high-dimensional embedding service using Google Cloud 
    Vertex AI.
    Ideal for production-grade semantic search and sentence embeddings.
    """
    
    def __init__(self, model_name: str = "text-embedding-004"):
        """
        Initialize the Vertex AI embedding model. 
        Assumes Google Cloud credentials are set in the environment.
        """
        self.__model = TextEmbeddingModel.from_pretrained(model_name)

    def get_embedding(self, text: str) -> np.ndarray:
        # Request the embedding from Vertex AI API
        embedding_result = self.__model.get_embeddings([text])[0]
        return np.array(embedding_result.values)

    def get_closest_words(
            self, 
            vector: np.ndarray, 
            top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Reverse search in high dimensions usually requires an indexed
        Vector Database.
        """
        raise NotImplementedError(
            "Reverse vocabulary search in high-dimensional models (Vertex AI) "
            "requires a Vector Database (e.g., Google Cloud Vector Search)."
        )