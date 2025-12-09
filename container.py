"""
Dependency Injection Container for MovExplainer.

This module provides a container class that implements a simple dependency injection
pattern to manage the lifecycle of application components.
"""

import os

from application.use_cases.analyze_position import AnalyzePosition
from infrastructure.engines.stockfish_engine import StockfishEngine
from infrastructure.llm.base_llm import ILLMService
from infrastructure.llm.ollama_llm import OllamaLLM
from infrastructure.llm.groq_llm import GroqLLM
from infrastructure.validators.chess_lib_validator import ChessLibValidator


class Container:
    """
    Simple DI Container to wire up the application.
    """

    def __init__(self):
        self._stockfish_path = self._resolve_stockfish_path()
        self._llm_provider = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "groq"
        self._ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        self._groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

        # Singleton-like instances
        self._engine = None
        self._llm = None
        self._validator = None

    def _resolve_stockfish_path(self) -> str:
        """Finds the Stockfish executable, checking env var first for cloud deployment."""
        # Check environment variable first (for cloud/Docker deployment)
        env_path = os.getenv("STOCKFISH_PATH")
        if env_path and os.path.exists(env_path):
            return env_path

        # Fallback to local Windows development path
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

    def get_llm(self) -> ILLMService:
        """Returns the LLM instance based on LLM_PROVIDER env var."""
        if not self._llm:
            if self._llm_provider == "groq":
                self._llm = GroqLLM(model=self._groq_model)
            else:
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
            llm_service=self.get_llm(),
            validator=self.get_validator(),
        )

    def close(self):
        """Cleanup resources."""
        if self._engine:
            self._engine.close()
