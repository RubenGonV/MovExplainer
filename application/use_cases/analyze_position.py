"""
Module for the AnalyzePosition use case.

This module defines the AnalyzePosition class, which orchestrates the process of
analyzing a chess position. It interacts with the engine service to get evaluations,
the validator to ensure move legality, and the LLM service to generate human-readable
explanations of the position and candidate moves.
"""

from typing import Dict, Any

from application.dto.analysis_request import AnalysisRequest
from application.dto.analysis_response import AnalysisResponse
from infrastructure.engines.base_engine import IEngineService
from infrastructure.llm.base_llm import ILLMService
from infrastructure.llm.prompt_builder import PromptBuilder
from infrastructure.validators.base_validator import IChessValidator
from domain.entities.evaluation import Evaluation


class AnalyzePosition:
    """
    Use case for analyzing a chess position and generating explanations.
    """

    def __init__(
        self,
        engine_service: IEngineService,
        llm_service: ILLMService,
        validator: IChessValidator,
    ):
        self._engine_service = engine_service
        self._llm_service = llm_service
        self._validator = validator

    def execute(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Execute the analysis use case.

        Args:
            request: The analysis request containing FEN and moves.

        Returns:
            AnalysisResponse containing the result and explanation.
        """
        try:
            # 1. Validate FEN
            if not self._validator.validate_fen(request.fen):
                return AnalysisResponse(success=False, error="Invalid FEN string")

            # 2. Validate Moves
            valid_moves = []
            for move in request.moves:
                try:
                    sanitized_move = self._validator.sanitize_move(move)
                    if self._validator.validate_move(request.fen, sanitized_move):
                        valid_moves.append(sanitized_move)
                except ValueError:
                    continue  # Skip invalid moves locally in the list

            if not valid_moves:
                return AnalysisResponse(success=False, error="No valid moves provided")

            # 3. Get evaluation for the current position (before move)
            eval_current = self._engine_service.evaluate(request.fen)

            # 4. Analyze candidate moves
            evals_after = self._engine_service.analyze_moves(request.fen, valid_moves)

            # 5. Prepare context for LLM
            context = self._build_context(
                request.fen, eval_current, evals_after, request.target_audience
            )

            # 6. Call LLM
            explanation = self._llm_service.explain(context)

            # 7. Construct response (picking the best move from the batch as a highlight)
            # Simple logic: best score
            best_move_uci = None
            best_score = -float("inf")

            # Helper to extract numeric score for comparison
            def get_score_value(ev: Evaluation) -> int:
                if ev.score.mate is not None:
                    # Prefer mate in fewer moves
                    mate_val = ev.score.mate
                    return (
                        100000 - abs(mate_val)
                        if mate_val > 0
                        else -100000 + abs(mate_val)
                    )
                return ev.score.cp if ev.score.cp is not None else 0

            for move, evaluation in evals_after.items():
                score_val = get_score_value(evaluation)
                if score_val > best_score:
                    best_score = score_val
                    best_move_uci = move

            return AnalysisResponse(
                success=True,
                explanation=explanation,
                best_move=best_move_uci,
                score=best_score if best_score != -float("inf") else None,
            )

        except (ValueError, RuntimeError, ConnectionError) as e:
            return AnalysisResponse(success=False, error=str(e))

    def _build_context(
        self,
        fen: str,
        eval_current: Evaluation,
        evals_after: Dict[str, Evaluation],
        target_audience: str,
    ) -> Dict[str, Any]:
        """
        Build the context dictionary for the LLM.
        """
        builder = PromptBuilder()
        builder.add_position(fen=fen)
        builder.add_evaluation(cp=eval_current.score.cp, mate=eval_current.score.mate)

        alternatives = []
        for move, ev in evals_after.items():
            alternatives.append(
                {
                    "move": move,
                    "evaluation": (
                        f"{ev.score.cp} centipawns"
                        if ev.score.cp is not None
                        else f"Mate in {ev.score.mate}"
                    ),
                    "cp": ev.score.cp,
                    "mate": ev.score.mate,
                    "pv": " ".join([str(m) for m in ev.pv]),
                }
            )
        builder.add_alternatives(alternatives)
        builder.add_custom_field("target_audience", target_audience)

        return builder.get_context()
