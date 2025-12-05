"""
Module for defining the base contract for chess validation services.
"""

from abc import ABC, abstractmethod
from typing import List


class IChessValidator(ABC):
    """
    Abstract base class defining the contract for chess validation services.

    Implementations must provide FEN validation, move legality checking,
    and input sanitization using a chess library.
    """

    @abstractmethod
    def validate_fen(self, fen: str) -> bool:
        """
        Validate a FEN string for correctness and legality.

        Args:
            fen: FEN string to validate

        Returns:
            True if FEN is valid and represents a legal position, False otherwise
        """

    @abstractmethod
    def validate_move(self, fen: str, move_uci: str) -> bool:
        """
        Validate if a move is legal in the given position.

        Args:
            fen: FEN string representing the position
            move_uci: Move in UCI notation (e.g., 'e2e4', 'e7e8q')

        Returns:
            True if the move is legal in the position, False otherwise

        Raises:
            ValueError: If FEN is invalid
        """

    @abstractmethod
    def sanitize_move(self, move_uci: str) -> str:
        """
        Clean and normalize a UCI move string.

        Args:
            move_uci: Move string to sanitize

        Returns:
            Sanitized and normalized UCI move string

        Raises:
            ValueError: If move format is invalid
        """

    @abstractmethod
    def get_legal_moves(self, fen: str) -> List[str]:
        """
        Get all legal moves for a given position.

        Args:
            fen: FEN string representing the position

        Returns:
            List of legal moves in UCI notation

        Raises:
            ValueError: If FEN is invalid
        """
