"""
Text generation service module.
Handles direct interaction with Vertex AI to retrieve single-token 
predictions and logprobs using the modern google-genai SDK.
"""

__version__ = "1.0.0"
__author__ = "Carlos Moreno Morera"

import math
from typing import Optional

from loguru import logger
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.config import get_settings
from app.ai.generator import TokenAlternative, GenServiceOutput


class TextGenerationService:
    """
    Service for generating text and retrieving token probabilities 
    using Vertex AI via the unified Google GenAI SDK.
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        """
        Initializes the GenAI Client for Vertex AI.
        
        Args:
            model_name (str): Gemini model version to use. Defaults to gemini-1.5-flash.
        """
        settings = get_settings()
        self.model_name = model_name
        self.region = settings.GCP_REGION
        
        logger.info(f"Initializing GenAI client for Vertex AI: {self.model_name} in {self.region}")
        
        self.client = genai.Client(
            vertexai=True,
            project=settings.GCP_PROJECT_ID,
            location=self.region
        )

    async def predict_next_token(
            self, 
            prompt: str, 
            temperature: Optional[float] = 0.0, 
            top_k: Optional[int] = 40, 
            top_p: Optional[float] = 0.95,
            num_alter_tokens: int = 5
    ) -> Optional[GenServiceOutput]:
        """
        Predicts exactly one next token for a given prompt and returns 
        its alternatives.
        
        Args:
            prompt (str): The input text.
            temperature (float): Controls randomness (0.0 = deterministic).
            top_k (int): Number of top tokens to consider.
            top_p (float): Cumulative probability cutoff.
            num_alter_tokens (int): Number of alternative tokens to return.
            
        Returns:
            GenServiceOutput containing the chosen token and a list of 
            alternative tokens with their probabilities, or None if the 
            request fails (e.g., safety block).
        """
        config = types.GenerateContentConfig(
            max_output_tokens=1,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            response_logprobs=True,
            logprobs=num_alter_tokens
        )
        
        logger.debug(
            f"Requesting next token (T={temperature}, Model={self.model_name})"
        )
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
        except APIError as e:
            logger.error(f"Vertex AI API Error: {str(e)}")
            raise 
        except Exception as e:
            logger.exception(
                f"Unexpected error during token generation: {str(e)}"
            )
            raise

        if not response.candidates:
            logger.warning(
                "No candidates returned. Response may have been blocked by safety settings."
            )
            return None

        candidate = response.candidates[0]
        
        if (candidate.finish_reason is not None
            and candidate.finish_reason != types.FinishReason.STOP 
            and candidate.finish_reason != types.FinishReason.MAX_TOKENS):
            logger.warning(
                f"Generation stopped unexpectedly. Finish reason: {candidate.finish_reason.name}"
            )
            return None

        result = GenServiceOutput(
            chosen_token=response.text or "", 
            alternatives=[]
        )
        
        if candidate.logprobs_result and candidate.logprobs_result.top_candidates:
            top_candidates_list = candidate.logprobs_result.top_candidates[0].candidates
            
            if top_candidates_list:
                for alt_candidate in top_candidates_list:
                    if (alt_candidate.log_probability is not None
                        and alt_candidate.token is not None):
                        prob_pct = math.exp(alt_candidate.log_probability) * 100
                    
                        result.alternatives.append(TokenAlternative(
                            token=alt_candidate.token,
                            probability=round(prob_pct, 4) 
                        ))
                
        return result