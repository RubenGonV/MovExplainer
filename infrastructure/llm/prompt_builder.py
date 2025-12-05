"""
Module for constructing structured prompts for LLMs.

This module provides a builder pattern implementation for creating consistent
and type-safe prompts for chess move explanations. It allows composing prompts
element by element (position, move, evaluation, etc.) before generating the
final string input for the LLM.
"""

from typing import Dict, Any, List, Optional
import json


class PromptBuilder:
    """
    Builder class for constructing structured prompts for chess explanations.

    Uses a fluent API to build prompts from structured data rather than
    string concatenation, ensuring consistency and type safety.

    Example:
        prompt = (PromptBuilder()
                  .add_position(fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
                  .add_move(uci="e2e4", san="e4")
                  .add_evaluation(cp=25, depth=15)
                  .build())
    """

    def __init__(self):
        """Initialize an empty prompt builder."""
        self._context: Dict[str, Any] = {}

    def add_position(
        self, fen: str, description: Optional[str] = None
    ) -> "PromptBuilder":
        """
        Add position information to the prompt.

        Args:
            fen: FEN string of the position
            description: Optional human-readable description (e.g., "starting position")

        Returns:
            Self for method chaining
        """
        self._context["position"] = {"fen": fen, "description": description}
        return self

    def add_move(self, uci: str, san: Optional[str] = None) -> "PromptBuilder":
        """
        Add the move being explained.

        Args:
            uci: Move in UCI notation
            san: Optional SAN notation for readability

        Returns:
            Self for method chaining
        """
        self._context["move"] = {"uci": uci, "san": san or uci}
        return self

    def add_evaluation(
        self,
        cp: Optional[int] = None,
        mate: Optional[int] = None,
        depth: Optional[int] = None,
        pv: Optional[List[str]] = None,
    ) -> "PromptBuilder":
        """
        Add evaluation information for the move.

        Args:
            cp: Centipawn evaluation
            mate: Mate in N moves (if applicable)
            depth: Search depth used
            pv: Principal variation (list of moves in SAN)

        Returns:
            Self for method chaining
        """
        eval_data = {}

        if mate is not None:
            eval_data["evaluation"] = f"Mate in {mate}"
            eval_data["mate"] = mate
        elif cp is not None:
            eval_data["evaluation"] = f"{cp} centipawns"
            eval_data["cp"] = cp

        if depth is not None:
            eval_data["depth"] = depth

        if pv:
            eval_data["principal_variation"] = " ".join(pv)

        self._context["evaluation"] = eval_data
        return self

    def add_alternatives(self, alternatives: List[Dict[str, Any]]) -> "PromptBuilder":
        """
        Add alternative moves for comparison.

        Args:
            alternatives: List of dicts with keys: 'move', 'evaluation', 'pv'

        Returns:
            Self for method chaining
        """
        self._context["alternatives"] = alternatives
        return self

    def add_custom_field(self, key: str, value: Any) -> "PromptBuilder":
        """
        Add a custom field to the context.

        Args:
            key: Field name
            value: Field value

        Returns:
            Self for method chaining
        """
        self._context[key] = value
        return self

    def build(self) -> str:
        """
        Build the final prompt string from the accumulated context.

        Returns:
            Formatted prompt string ready for LLM

        Example:
            You are a chess expert. Explain the following chess move in a clear and educational way.

            Position: r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 1 3
            Move: Nf3
            Evaluation: +0.2 (Depth: 20, PV: Nf3 Nc6 Bb5 a6 Bxc6 dxc6 d3 Bd6 O-O Ne7)
            Alternatives:
            - Move: Nc3, Evaluation: +0.1
            - Move: d4, Evaluation: +0.3
            Explanation:
            The move Nf3 is a standard developing move in chess.
            It develops the knight to a central square, controls the e5 and d4 squares,
            and prepares for castling. It is a solid and flexible move that leads to an open game.
        """

        # Create a structured prompt template
        prompt_parts = [
            "You are a chess expert. ",
            "Explain the following chess move in a clear and educational way.",
            "",
        ]

        # Add position info
        if "position" in self._context:
            pos = self._context["position"]
            if isinstance(pos, dict):
                if pos.get("description"):
                    prompt_parts.append(f"Position: {pos['description']}")
                if "fen" in pos:
                    prompt_parts.append(f"FEN: {pos['fen']}")
            else:
                prompt_parts.append(f"Position: {pos}")
            prompt_parts.append("")

        # Add move info
        if "move" in self._context:
            move = self._context["move"]
            if isinstance(move, dict):
                prompt_parts.append(
                    f"Move played: {move.get('san', 'N/A')} ({move.get('uci', 'N/A')})"
                )
            else:
                prompt_parts.append(f"Move played: {move}")
            prompt_parts.append("")

        # Add evaluation
        if "evaluation" in self._context:
            eval_data = self._context["evaluation"]
            if isinstance(eval_data, dict):
                prompt_parts.append(f"Evaluation: {eval_data.get('evaluation', 'N/A')}")

                if "depth" in eval_data:
                    prompt_parts.append(f"Analysis depth: {eval_data['depth']}")

                if "principal_variation" in eval_data:
                    prompt_parts.append(
                        f"Best continuation: {eval_data['principal_variation']}"
                    )
            else:
                prompt_parts.append(f"Evaluation: {eval_data}")

            prompt_parts.append("")

        # Add alternatives
        if "alternatives" in self._context:
            prompt_parts.append("Alternative moves:")
            for alt in self._context["alternatives"]:
                prompt_parts.append(
                    f"  - {alt.get('move', 'N/A')}: {alt.get('evaluation', 'N/A')}"
                )
            prompt_parts.append("")

        # Add instruction
        prompt_parts.extend(
            [
                "Please explain:",
                "1. What this move accomplishes",
                "2. The key ideas behind it",
                "3. How it compares to alternatives (if provided)",
                "4. Any tactical or strategic themes involved",
                "",
                "Keep the explanation concise but informative.",
            ]
        )

        return "\n".join(prompt_parts)

    def get_context(self) -> Dict[str, Any]:
        """
        Get the raw context dictionary.

        Returns:
            Dictionary containing all accumulated context
        """
        return self._context.copy()

    def to_json(self) -> str:
        """
        Export the context as JSON.

        Returns:
            JSON string representation of the context
        """
        return json.dumps(self._context, indent=2)
