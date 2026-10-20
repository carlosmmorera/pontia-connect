"""
High Dimension Embedding Service module.

This module defines a service based on EmbeddingService for managing
embeddings by using a cloud-based high-dimensional model with Google
Cloud Vertex AI via the unified google-genai SDK.
"""

__version__ = "2.0.0"
__author__ = "Carlos Moreno Morera"

from typing import List, Tuple, Optional
import numpy as np
from loguru import logger

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import get_settings
from app.ai.embeddings import EmbeddingService


class HighDimEmbeddingService(EmbeddingService):
    """
    Cloud-based high-dimensional embedding service using Google Cloud 
    Vertex AI (google-genai).
    Ideal for production-grade semantic search and sentence embeddings.
    """
    
    def __init__(
        self, 
        model_name: str = "text-embedding-004",
        output_dimensionality: Optional[int] = None
    ):
        """
        Initializes the GenAI Client for the Vertex AI embedding model.
        
        Args:
            model_name (str): The name of the embedding model.
            output_dimensionality (int, optional): Truncates the
                embedding to this dimension (supported by 
                text-embedding-004+). Lower dimensions save Vector DB 
                storage costs.
        """
        settings = get_settings()
        self.model_name = model_name
        self.output_dimensionality = output_dimensionality
        self.region = settings.GCP_REGION
        
        logger.info(
            f"Initializing Embedding client: {self.model_name} in {self.region}"
        )
        
        self.client = genai.Client(
            vertexai=True,
            project=settings.GCP_PROJECT_ID,
            location=self.region
        )

    def get_embedding(
        self, 
        text: str
    ) -> np.ndarray:
        """
        Synchronously requests the embedding for a given text.
        
        Args:
            text (str): The input string to embed.
                
        Returns:
            np.ndarray: A 1D numpy array containing the embedding vectors in float32.
        """
        config_kwargs = {}
        if self.output_dimensionality:
            config_kwargs["output_dimensionality"] = self.output_dimensionality
            
        config = types.EmbedContentConfig(**config_kwargs) if config_kwargs else None

        logger.debug(f"Requesting embedding for text (Model={self.model_name})")
        
        try:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=text,
                config=config
            )
        except APIError as e:
            logger.error(f"Vertex AI Embedding API Error: {str(e)}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during embedding generation")
            raise

        if not response.embeddings or not response.embeddings[0].values:
            raise ValueError("API returned an empty embedding response.")

        return np.array(response.embeddings[0].values, dtype=np.float32)

    async def get_embedding_async(
        self, 
        text: str
    ) -> np.ndarray:
        """
        Asynchronously requests the embedding. 
        Ideal for high-throughput applications to avoid blocking the
        event loop.
        """
        config_kwargs = {}
        if self.output_dimensionality:
            config_kwargs["output_dimensionality"] = self.output_dimensionality
            
        config = types.EmbedContentConfig(**config_kwargs) if config_kwargs else None

        try:
            response = await self.client.aio.models.embed_content(
                model=self.model_name,
                contents=text,
                config=config
            )
        except Exception as e:
            logger.error(f"Async embedding generation failed: {str(e)}")
            raise

        if not response.embeddings or not response.embeddings[0].values:
            raise ValueError("API returned an empty embedding response.")

        return np.array(response.embeddings[0].values, dtype=np.float32)

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
            "requires a Vector Database (e.g., Qdrant, Pinecone)."
        )