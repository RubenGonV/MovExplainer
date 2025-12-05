"""
Stockfish chess engine implementation for the MovExplainer project.

This module provides a concrete implementation of the IEngineService interface
using the Stockfish chess engine. It implements the Singleton pattern to ensure
a single engine process is shared across the application, and supports the
context manager protocol for proper resource management.

Classes:
    StockfishEngine: Singleton chess engine service using Stockfish.

Example:
    Using the engine with context manager (recommended):
    >>> with StockfishEngine() as engine:
    ...     evaluation = engine.evaluate("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    ...     print(evaluation.score)
"""

import os
from threading import Lock
from typing import Dict, List, Optional

import chess
import chess.engine

from domain.entities.evaluation import Evaluation
from domain.entities.move import Move
from domain.value_objects.score import Score
from infrastructure.engines.base_engine import IEngineService


class StockfishEngine(IEngineService):
    """
    Concrete implementation of IEngineService using the Stockfish chess engine.

    Implements Singleton pattern to manage a single engine process across
    the application lifecycle. Supports context manager protocol for
    proper resource cleanup.

    Example:
        # Using context manager (recommended)
        with StockfishEngine() as engine:
            eval = engine.evaluate(fen, depth=15)

        # Manual management
        engine = StockfishEngine()
        eval = engine.evaluate(fen)
        engine.close()
    """

    _instance: Optional["StockfishEngine"] = None
    _lock: Lock = Lock()
    _engine_process: Optional[chess.engine.SimpleEngine] = None
    _engine_path: Optional[str] = None
    _initialized: bool = False

    def __new__(cls, engine_path: Optional[str] = None):
        """
        Singleton pattern implementation.

        Args:
            engine_path: Optional custom path to Stockfish executable.
                        If not provided, uses default path relative to project root.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    @classmethod
    def reset_singleton(cls) -> None:
        """
        Reset the singleton instance. EXCLUSIVELY FOR TESTING.
        """
        with cls._lock:
            if cls._instance:
                cls._instance.close()
            cls._instance = None

    def __init__(self, engine_path: Optional[str] = None):
        """
        Initialize the Stockfish engine.

        Args:
            engine_path: Optional custom path to Stockfish executable.
                        If not provided, uses default path or environment variable.
        """
        # Only initialize once (Singleton pattern)
        if self._initialized:
            return

        # Determine engine path
        if engine_path:
            self._engine_path = engine_path
        elif os.environ.get("STOCKFISH_PATH"):
            self._engine_path = os.environ["STOCKFISH_PATH"]
        else:
            # Default path relative to project root
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            engine_rel_path = os.path.join(
                "infrastructure",
                "engines",
                "stockfish-windows-x86-64-avx2",
                "stockfish",
                "stockfish-windows-x86-64-avx2.exe",
            )
            self._engine_path = os.path.join(base_dir, engine_rel_path)

        self._initialized = True

    def _ensure_engine_started(self) -> None:
        """
        Lazy initialization: Start the engine process if not already running.

        Raises:
            FileNotFoundError: If engine executable not found
            RuntimeError: If engine fails to start
        """
        if self._engine_process is not None:
            return

        if not os.path.isfile(self._engine_path):
            raise FileNotFoundError(
                f"Stockfish engine not found at: {self._engine_path}\n"
                f"Please ensure the file exists or set STOCKFISH_PATH environment variable."
            )

        try:
            self._engine_process = chess.engine.SimpleEngine.popen_uci(
                self._engine_path
            )
        except Exception as e:
            raise RuntimeError(f"Failed to start Stockfish engine: {e}") from e

    def evaluate(self, fen: str, depth: int = 15) -> Evaluation:
        """
        Evaluate a single chess position.

        Args:
            fen: FEN string representing the position
            depth: Search depth for the engine (default: 15)

        Returns:
            Evaluation object containing score and principal variation

        Raises:
            ValueError: If FEN is invalid
            RuntimeError: If engine fails to evaluate
        """
        self._ensure_engine_started()

        # Validate and load position
        try:
            board = chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN: {fen}") from e

        # Analyze position
        try:
            info = self._engine_process.analyse(board, chess.engine.Limit(depth=depth))
        except Exception as e:
            raise RuntimeError(f"Engine analysis failed: {e}") from e

        # Extract score (from perspective of side to move)
        raw_score = info["score"].pov(board.turn)

        # Convert to domain Score object
        if raw_score.is_mate():
            score = Score(mate=raw_score.mate())
        else:
            score = Score(cp=raw_score.score())

        # Extract principal variation
        pv_moves = info.get("pv", [])[:5]  # Limit to 5 moves
        pv = self._convert_pv_to_moves(board, pv_moves)

        return Evaluation(score=score, depth=depth, pv=pv)

    def analyze_moves(
        self, fen: str, candidate_moves: List[str], depth: int = 15
    ) -> Dict[str, Evaluation]:
        """
        Analyze multiple candidate moves from a position.

        Args:
            fen: FEN string representing the position
            candidate_moves: List of moves in UCI notation (e.g., ['e2e4', 'd2d4'])
            depth: Search depth for the engine (default: 15)

        Returns:
            Dictionary mapping UCI move strings to their Evaluation objects

        Raises:
            ValueError: If FEN is invalid or moves are malformed
            RuntimeError: If engine fails to analyze
        """
        self._ensure_engine_started()

        # Validate and load position
        try:
            board = chess.Board(fen)
        except ValueError as e:
            raise ValueError(f"Invalid FEN: {fen}") from e

        results = {}

        for move_uci in candidate_moves:
            try:
                move = chess.Move.from_uci(move_uci)
            except ValueError:
                # Skip invalid UCI moves
                continue

            if move not in board.legal_moves:
                # Skip illegal moves
                continue

            # Make the move on a copy of the board
            new_board = board.copy()
            new_board.push(move)

            # Analyze the resulting position
            try:
                info = self._engine_process.analyse(
                    new_board, chess.engine.Limit(depth=depth)
                )
            except Exception as e:
                raise RuntimeError(
                    f"Engine analysis failed for move {move_uci}: {e}"
                ) from e

            # Extract score (from perspective of the player who made the move)
            raw_score = info["score"].pov(board.turn)

            # Convert to domain Score object
            if raw_score.is_mate():
                score = Score(mate=raw_score.mate())
            else:
                score = Score(cp=raw_score.score())

            # Extract principal variation
            pv_moves = info.get("pv", [])[:5]
            pv = self._convert_pv_to_moves(new_board, pv_moves)

            results[move_uci] = Evaluation(score=score, depth=depth, pv=pv)

        return results

    def _convert_pv_to_moves(
        self, board: chess.Board, pv_moves: List[chess.Move]
    ) -> List[Move]:
        """
        Convert a list of chess.Move objects to domain Move objects with SAN notation.

        Args:
            board: Current board position
            pv_moves: List of chess.Move objects from engine

        Returns:
            List of domain Move objects with UCI and SAN notation
        """
        result = []
        temp_board = board.copy()

        for chess_move in pv_moves:
            # Get SAN notation before making the move
            san = temp_board.san(chess_move)
            uci = chess_move.uci()

            result.append(Move(uci=uci, san=san))
            temp_board.push(chess_move)

        return result

    def close(self) -> None:
        """
        Clean up engine resources and terminate the engine process.

        Idempotent - safe to call multiple times.
        """
        if self._engine_process is not None:
            try:
                self._engine_process.quit()
            except (OSError, RuntimeError):
                # Ignore errors during cleanup
                pass
            finally:
                self._engine_process = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.close()
        return False

    @property
    def engine_path(self) -> Optional[str]:
        """Get the path to the Stockfish executable."""
        return self._engine_path

    @property
    def is_engine_running(self) -> bool:
        """Check if the engine process is currently running."""
        return self._engine_process is not None
