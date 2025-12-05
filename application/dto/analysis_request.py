"""
Module defining the AnalysisRequest DTO.

This module contains the AnalysisRequest class, which encapsulates the data
required to perform a chess analysis.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AnalysisRequest:
    """
    Data Transfer Object for analysis requests.
    """

    fen: str
    moves: List[str]
    target_audience: Optional[str] = "beginner"
