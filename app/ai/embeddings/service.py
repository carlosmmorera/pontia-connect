"""
Embedding services module.

This module defines an abstract base class for embedding services, 
ensuring a consistent interface across different embedding providers 
(e.g., local low-dimensional models vs. cloud-based high-dimensional
models).
"""

__version__ = "1.0"
__author__ = "Carlos Moreno Morera"

from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np


class EmbeddingService(ABC):
    """
    Abstract base class for all embedding services.
    Enforces a common interface for getting embeddings and computing 
    similarities.
    """

    @abstractmethod
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Convert a text string into a numerical vector (embedding).
        
        Args:
            text (str): The input text (word or sentence).
            
        Returns:
            np.ndarray: The vector representation of the text.
        """
        pass

    @abstractmethod
    def get_closest_words(
        self, 
        vector: np.ndarray, 
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find the closest words to a given vector. 
        Useful for demonstrating vector arithmetic
        (e.g., King - Man + Woman = Queen).
        
        Args:
            vector (np.ndarray): The target vector.
            top_n (int): Number of closest words to return.
            
        Returns:
            List[Tuple[str, float]]: A list of tuples containing the 
            word and its similarity score.
        """
        pass

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate the cosine similarity between two vectors.
        This is a shared utility method available to all child classes.
        
        Args:
            vec1 (np.ndarray): First vector.
            vec2 (np.ndarray): Second vector.
            
        Returns:
            float: Cosine similarity score [-1.0, 1.0].
        """
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        return float(dot_product / (norm_a * norm_b))