"""
Low Dimension Embedding Service module.

This module defines a service based on EmbeddingService for managing
embeddings by using a local low-dimensional model from Gensim and GloVe.
"""

__version__ = "1.0"
__author__ = "Carlos Moreno Morera"

from typing import List, Tuple, cast
import numpy as np
from loguru import logger

import gensim.downloader as api
from gensim.models import KeyedVectors

from app.ai.embeddings import EmbeddingService


class LowDimEmbeddingService(EmbeddingService):
    """
    Local low-dimensional embedding service using Gensim and GloVe.
    It is recommended for demonstrating word analogies in real-time
    without latency.
    """
    
    def __init__(self, model_name: str = "glove-wiki-gigaword-50") -> None:
        """
        Initialize the local embedding model. Will download the model on
        first run.
        """
        try:
            self.__model: KeyedVectors = cast(KeyedVectors, api.load(model_name))
            self.__vector_size: int = self.__model.vector_size
        except Exception as e:
            logger.error(f"Fallo al cargar el modelo {model_name}. Verifica GENSIM_DATA_DIR. Detalles: {e}")
            raise RuntimeError(f"Error crítico cargando modelo de embeddings: {e}")

    def get_embedding(self, text: str) -> np.ndarray:
        # Preprocess text to lowercase as GloVe vocabulary is case-sensitive
        clean_text = text.lower().strip()

        if clean_text in self.__model:
            return self.__model[clean_text]
        
        # Return a zero vector if the word is Out Of Vocabulary (OOV)
        return np.zeros(self.__vector_size, dtype=np.float32)

    def get_closest_words(
            self, 
            vector: np.ndarray, 
            top_n: int = 5
    ) -> List[Tuple[str, float]]:
        # Uses Gensim's built-in vector search functionality
        return self.__model.similar_by_vector(vector, topn=top_n)