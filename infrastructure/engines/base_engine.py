"""
Module defining the abstract base class for chess engine services.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from domain.entities.evaluation import Evaluation


class IEngineService(ABC):
    """
    Abstract base class defining the contract for chess engine services.

    Implementations must provide position evaluation and move analysis capabilities.
    """

    @abstractmethod
    def evaluate(self, fen: str, depth: int = 15) -> Evaluation:
        """
        Evaluate a single chess position.

        Args:
            fen: FEN string representing the position
            depth: Search depth for the engine

        Returns:
            Evaluation object containing score and principal variation

        Raises:
            ValueError: If FEN is invalid
            RuntimeError: If engine fails to evaluate
        """

    @abstractmethod
    def analyze_moves(
        self, fen: str, candidate_moves: List[str], depth: int = 15
    ) -> Dict[str, Evaluation]:
        """
        Analyze multiple candidate moves from a position.

        Args:
            fen: FEN string representing the position
            candidate_moves: List of moves in UCI notation (e.g., ['e2e4', 'd2d4'])
            depth: Search depth for the engine

        Returns:
            Dictionary mapping UCI move strings to their Evaluation objects

        Raises:
            ValueError: If FEN is invalid or moves are malformed
            RuntimeError: If engine fails to analyze
        """

    @abstractmethod
    def close(self) -> None:
        """
        Clean up engine resources and terminate the engine process.

        Should be called when the engine is no longer needed.
        Implementations should be idempotent (safe to call multiple times).
        """
