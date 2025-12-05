"""
Chess Validator Implementation using python-chess.

This module provides a concrete implementation of the IChessValidator interface,
using the python-chess library for accurate move generation and validation.
"""

from typing import List

import chess
from infrastructure.validators.base_validator import IChessValidator


class ChessLibValidator(IChessValidator):
    """
    Concrete implementation of IChessValidator using the python-chess library.

    Provides FEN validation, move legality checking, and input sanitization.
    """

    def validate_fen(self, fen: str) -> bool:
        """
        Validate a FEN string for correctness and legality.

        Args:
            fen: FEN string to validate

        Returns:
            True if FEN is valid and represents a legal position, False otherwise
        """
        # Enforce strict FEN format (must have 6 fields)
        if len(fen.split()) != 6:
            return False

        try:
            chess.Board(fen)
            return True
        except ValueError:
            return False

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
        try:
            board = chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN: {fen}") from e

        try:
            move = chess.Move.from_uci(move_uci)
            return move in board.legal_moves
        except ValueError:
            # Invalid UCI format
            return False

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
        # Remove whitespace and convert to lowercase
        sanitized = move_uci.strip().lower()

        # Validate UCI format using python-chess
        try:
            move = chess.Move.from_uci(sanitized)
            # Return the canonical UCI representation
            return move.uci()
        except ValueError as e:
            raise ValueError(f"Invalid UCI move format: {move_uci}") from e

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
        try:
            board = chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN: {fen}") from e

        return [move.uci() for move in board.legal_moves]
