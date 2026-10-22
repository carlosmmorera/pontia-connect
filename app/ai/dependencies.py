"""
Dependency Injection and Service Locator module.
Ensures heavy AI models and cloud clients are instantiated as Singletons.
"""

from functools import lru_cache
from loguru import logger

from app.ai.embeddings import LowDimEmbeddingService, HighDimEmbeddingService
from app.ai.generator import TextGenerationService

@lru_cache(maxsize=1)
def get_low_dim_service() -> LowDimEmbeddingService:
    """Provides a singleton instance of the Low Dimension Service."""
    logger.info("Instantiating LowDimEmbeddingService (Gensim)...")
    return LowDimEmbeddingService()

@lru_cache(maxsize=1)
def get_high_dim_service() -> HighDimEmbeddingService | None:
    """Provides a singleton instance of the High Dimension Service."""
    logger.info("Instantiating HighDimEmbeddingService (Vertex AI)...")
    try:
        return HighDimEmbeddingService()
    except Exception as e:
        logger.warning(f"HighDim service unavailable (Check GCP credentials): {e}")
        return None

@lru_cache(maxsize=1)
def get_generator_service() -> TextGenerationService | None:
    """Provides a singleton instance of the Text Generation Service."""
    logger.info("Instantiating TextGenerationService (Vertex AI)...")
    try:
        return TextGenerationService()
    except Exception as e:
        logger.warning(f"TextGenerationService unavailable (Check GCP credentials): {e}")
        return None