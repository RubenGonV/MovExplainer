"""
Pydantic models for request/response validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnalysisRequestModel(BaseModel):
    """
    Analysis request model.
    It contains:
        - the FEN string of the chess position,
        - a list of moves to analyze (UCI format),
        - an optional target audience.
    """

    fen: str = Field(..., description="FEN string of the chess position", min_length=10)
    moves: List[str] = Field(
        ..., description="List of moves to analyze (UCI format)", min_length=0
    )
    target_audience: Optional[str] = Field(
        "beginner", description="Target audience for the explanation"
    )


class AnalysisResponseModel(BaseModel):
    """
    Analysis response model.
    It contains:
        - a success flag,
        - an optional explanation,
        - an optional error message,
        - an optional best move,
        - an optional score.
    """

    success: bool
    explanation: Optional[str] = None
    error: Optional[str] = None
    best_move: Optional[str] = None
    score: Optional[int] = None
