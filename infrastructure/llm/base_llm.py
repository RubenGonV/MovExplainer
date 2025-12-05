"""
Module defining the base interface for Large Language Model (LLM) services.

This module provides the abstract base class `ILLMService` which establishes the
contract for any LLM implementation used within the MovExplainer application.
It ensures consistent interaction for generating natural language explanations
from structured chess data.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ILLMService(ABC):
    """
    Abstract base class defining the contract for Large Language Model services.

    Implementations must provide natural language explanation generation
    based on structured chess context.
    """

    @abstractmethod
    def explain(self, context: Dict[str, Any]) -> str:
        """
        Generate a natural language explanation from structured context.

        Args:
            context: Dictionary containing chess-related information such as:
                - 'position': FEN or description of the position
                - 'move': Move being explained
                - 'evaluation': Evaluation data
                - 'alternatives': Alternative moves and their evaluations
                - Any other relevant context

        Returns:
            Natural language explanation as a string

        Raises:
            ValueError: If context is invalid or missing required fields
            RuntimeError: If LLM service fails to generate explanation
            ConnectionError: If LLM service is unreachable
        """

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM service is available and reachable.

        Returns:
            True if service is available, False otherwise

        Note:
            This should be a lightweight check (e.g., ping or health endpoint).
            It should not generate any actual content.
        """
