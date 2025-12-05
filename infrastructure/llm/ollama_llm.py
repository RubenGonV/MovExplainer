"""
Ollama LLM Service Implementation.

This module provides a concrete implementation of the ILLMService interface
using the Ollama library to interact with local LLMs.
"""

import time
from typing import Dict, Any, Optional

import ollama

from infrastructure.llm.base_llm import ILLMService
from infrastructure.llm.prompt_builder import PromptBuilder


class OllamaLLM(ILLMService):
    """
    Concrete implementation of ILLMService using Ollama.

    Provides natural language explanations for chess positions and moves
    using a local Ollama instance.

    Example:
        llm = OllamaLLM(model="mistral")
        if llm.is_available():
            context = {
                'position': 'starting position',
                'move': 'e4',
                'evaluation': '+0.25'
            }
            explanation = llm.explain(context)
    """

    def __init__(
        self,
        model: str = "mistral",
        host: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the Ollama LLM service.

        Args:
            model: Name of the Ollama model to use (default: "mistral")
            host: Optional Ollama host URL (default: uses Ollama's default)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts for transient failures (default: 3)
        """
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

        # Initialize Ollama client
        if host:
            self.client = ollama.Client(host=host)
        else:
            self.client = ollama.Client()

    def explain(self, context: Dict[str, Any]) -> str:
        """
        Generate a natural language explanation from structured context.

        Args:
            context: Dictionary containing chess-related information.
                    Can be a raw dict or output from PromptBuilder.

        Returns:
            Natural language explanation as a string

        Raises:
            ValueError: If context is invalid or missing required fields
            RuntimeError: If LLM service fails to generate explanation
            ConnectionError: If LLM service is unreachable
        """
        if not context:
            raise ValueError("Context cannot be empty")

        # Build prompt from context
        prompt = self._build_prompt(context)

        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={
                        "temperature": 0.7,
                        "top_p": 0.9,
                    },
                )

                return response["response"].strip()

            except ollama.ResponseError as e:
                last_exception = e
                if e.status_code >= 500:
                    # Server error - retry with backoff
                    if attempt < self.max_retries - 1:
                        time.sleep(2**attempt)  # Exponential backoff: 1s, 2s, 4s
                        continue
                else:
                    # Client error - don't retry
                    raise RuntimeError(f"Ollama API error: {e}") from e

            except ConnectionError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(2**attempt)
                    continue
                else:
                    raise ConnectionError(
                        f"Cannot connect to Ollama service: {e}"
                    ) from e

            except Exception as e:
                raise RuntimeError(
                    f"Unexpected error during LLM generation: {e}"
                ) from e

        # If we exhausted all retries
        raise RuntimeError(
            f"Failed to generate explanation after {self.max_retries} attempts"
        ) from last_exception

    def is_available(self) -> bool:
        """
        Check if the LLM service is available and reachable.

        Returns:
            True if service is available, False otherwise
        """
        try:
            # Try to list models as a lightweight health check
            self.client.list()
            return True
        except (ollama.ResponseError, ConnectionError):
            return False

    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build a prompt string from the context dictionary.

        Args:
            context: Context dictionary

        Returns:
            Formatted prompt string
        """
        # If context looks like it came from PromptBuilder, use it directly
        if "position" in context or "move" in context or "evaluation" in context:
            builder = PromptBuilder()

            # Reconstruct from context
            if "position" in context:
                pos = context["position"]
                if isinstance(pos, dict):
                    builder.add_position(
                        fen=pos.get("fen", ""), description=pos.get("description")
                    )
                else:
                    builder.add_custom_field("position", pos)

            if "move" in context:
                move = context["move"]
                if isinstance(move, dict):
                    builder.add_move(uci=move.get("uci", ""), san=move.get("san"))
                else:
                    builder.add_custom_field("move", move)

            if "evaluation" in context:
                eval_data = context["evaluation"]
                if isinstance(eval_data, dict):
                    builder.add_evaluation(
                        cp=eval_data.get("cp"),
                        mate=eval_data.get("mate"),
                        depth=eval_data.get("depth"),
                        pv=eval_data.get("pv"),
                    )
                else:
                    builder.add_custom_field("evaluation", eval_data)

            if "alternatives" in context:
                builder.add_alternatives(context["alternatives"])

            return builder.build()

        # Fallback: create a simple prompt from raw context
        prompt_parts = [
            "You are a chess expert. Explain the following chess situation:",
            "",
        ]

        for key, value in context.items():
            prompt_parts.append(f"{key}: {value}")

        prompt_parts.append("")
        prompt_parts.append("Provide a clear and educational explanation.")

        return "\n".join(prompt_parts)
