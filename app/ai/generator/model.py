"""
Model service module.
It contains all data models needed in TextGenerationService
"""

__version__ = "1.0.0"
__author__ = "Carlos Moreno Morera"

from pydantic import BaseModel
from typing import List


class TokenAlternative(BaseModel):
    token: str
    probability: float


class GenServiceOutput(BaseModel):
    chosen_token: str
    alternatives: List[TokenAlternative]