"""
Dependency Injection Container for MovExplainer.

This module provides a container class that implements a simple dependency injection
pattern to manage the lifecycle of application components.
"""

import os

from application.use_cases.analyze_position import AnalyzePosition
from infrastructure.engines.stockfish_engine import StockfishEngine
from infrastructure.llm.ollama_llm import OllamaLLM
from infrastructure.validators.chess_lib_validator import ChessLibValidator


class Container:
    """
    Simple DI Container to wire up the application.
    """

    def __init__(self):
        self._stockfish_path = self._resolve_stockfish_path()
        self._ollama_model = os.getenv("OLLAMA_MODEL", "mistral")

        # Singleton-like instances
        self._engine = None
        self._llm = None
        self._validator = None

    def _resolve_stockfish_path(self) -> str:
        """Finds the Stockfish executable in the default location."""
        # Assuming run from root
        base_path = os.path.dirname(os.path.abspath(__file__))
        stockfish_rel_path = os.path.join(
            "infrastructure",
            "engines",
            "stockfish-windows-x86-64-avx2",
            "stockfish",
            "stockfish-windows-x86-64-avx2.exe",
        )
        path = os.path.join(base_path, stockfish_rel_path)

        if not os.path.exists(path):
            # Fallback or warning could go here
            pass
        return path

    def get_stockfish_engine(self) -> StockfishEngine:
        """Returns the StockfishEngine instance, creating it if necessary."""
        if not self._engine:
            self._engine = StockfishEngine(self._stockfish_path)
        return self._engine

    def get_ollama_llm(self) -> OllamaLLM:
        """Returns the OllamaLLM instance, creating it if necessary."""
        if not self._llm:
            self._llm = OllamaLLM(model=self._ollama_model)
        return self._llm

    def get_validator(self) -> ChessLibValidator:
        """Returns the ChessLibValidator instance, creating it if necessary."""
        if not self._validator:
            self._validator = ChessLibValidator()
        return self._validator

    def get_analyze_position_use_case(self) -> AnalyzePosition:
        """Creates and returns the AnalyzePosition use case with dependencies."""
        return AnalyzePosition(
            engine_service=self.get_stockfish_engine(),
            llm_service=self.get_ollama_llm(),
            validator=self.get_validator(),
        )

    def close(self):
        """Cleanup resources."""
        if self._engine:
            self._engine.close()
