from dataclasses import dataclass, field
from typing import List
from domain.value_objects.score import Score
from domain.entities.move import Move

@dataclass(frozen=True)
class Evaluation:
    """
    Entity representing the evaluation of a specific position/move.
    """
    score: Score
    depth: int
    pv: List[Move] = field(default_factory=list)

    def __str__(self):
        score_str = f"Mate in {self.score.mate}" if self.score.mate is not None else f"{self.score.cp} cp"
        return f"Eval: {score_str} (depth {self.depth})"
