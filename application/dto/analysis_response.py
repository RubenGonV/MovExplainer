"""
Module defining the AnalysisResponse DTO.

This module contains the AnalysisResponse class, which encapsulates the results
of a chess analysis operation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AnalysisResponse:
    """
    Data Transfer Object for analysis responses.
    """

    success: bool
    explanation: Optional[str] = None
    error: Optional[str] = None
    best_move: Optional[str] = None
    score: Optional[int] = None
