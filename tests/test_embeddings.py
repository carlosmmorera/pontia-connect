"""
Unit tests for the Embeddings module.

This module tests the logic of the EmbeddingService classes using mocked
dependencies to avoid network calls and heavy downloads during CI/CD.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from app.ai.embeddings import (
    EmbeddingService, 
    LowDimEmbeddingService, 
    HighDimEmbeddingService
)


class DummyEmbeddingService(EmbeddingService):
    """A minimal implementation of the abstract class to test shared methods."""
    def get_embedding(self, text: str) -> np.ndarray:
        return np.array([1.0, 0.0])
        
    def get_closest_words(self, vector: np.ndarray, top_n: int = 5):
        return []


def test_cosine_similarity():
    """Test the shared cosine similarity math logic."""
    service = DummyEmbeddingService()
    
    # Perpendicular vectors should have similarity 0
    vec1 = np.array([1.0, 0.0])
    vec2 = np.array([0.0, 1.0])
    assert service.cosine_similarity(vec1, vec2) == 0.0
    
    # Identical vectors should have similarity 1
    vec3 = np.array([1.0, 1.0])
    assert np.isclose(service.cosine_similarity(vec3, vec3), 1.0)
    
    # Opposite vectors should have similarity -1
    vec4 = np.array([-1.0, -1.0])
    assert np.isclose(service.cosine_similarity(vec3, vec4), -1.0)


@patch("app.ai.embeddings.lowdimservice.api.load")
def test_low_dim_embedding_service(mock_api_load):
    """Test the Gensim-based LowDimEmbeddingService with a mocked model."""
    
    # Setup the mock to simulate Gensim's KeyedVectors
    mock_model = MagicMock()
    mock_model.vector_size = 50
    # Simulate that the word "king" is in the vocabulary
    mock_model.__contains__.side_effect = lambda word: word == "king"
    mock_model.__getitem__.side_effect = lambda word: (np.ones(50) 
                                                       if word == "king"
                                                       else np.zeros(50))
    mock_api_load.return_value = mock_model
    
    service = LowDimEmbeddingService("dummy-model")
    
    # Test known word
    king_vec = service.get_embedding("King")
    assert king_vec.shape == (50,)
    assert king_vec[0] == 1.0
    
    # Test Out-Of-Vocabulary (OOV) word
    oov_vec = service.get_embedding("asdfgh")
    assert oov_vec.shape == (50,)
    assert oov_vec[0] == 0.0


@patch("app.ai.embeddings.highdimservice.TextEmbeddingModel.from_pretrained")
def test_high_dim_embedding_service(mock_from_pretrained):
    """Test the Vertex AI HighDimEmbeddingService with a mocked SDK."""
    
    # Setup the mock Vertex AI model response
    mock_model_instance = MagicMock()
    mock_embedding = MagicMock()
    mock_embedding.values = [0.1] * 768
    mock_model_instance.get_embeddings.return_value = [mock_embedding]
    
    mock_from_pretrained.return_value = mock_model_instance
    
    service = HighDimEmbeddingService("dummy-vertex-model")
    
    # Test getting an embedding
    vec = service.get_embedding("Hello Generative AI")
    assert vec.shape == (768,)
    assert vec[0] == 0.1
    
    # Test that reverse search raises NotImplementedError
    with pytest.raises(NotImplementedError):
        service.get_closest_words(vec)