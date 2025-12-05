from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Score:
    """
    Value Object representing a chess position evaluation score.
    """
    cp: Optional[int] = None  # Centipawns
    mate: Optional[int] = None # Moves to mate

    def __post_init__(self):
        if self.cp is None and self.mate is None:
            raise ValueError("Score must have either cp or mate value")
        if self.cp is not None and self.mate is not None:
            raise ValueError("Score cannot have both cp and mate value")

    def to_centipawns(self) -> int:
        """
        Normalizes the score to centipawns.
        Mates are converted to +/- 10000 adjusted by mate distance.
        """
        if self.mate is not None:
            if self.mate > 0:
                return 10000 - self.mate
            else:
                return -10000 - self.mate
        
        # Should be safe because of __post_init__ check, but for type checker:
        if self.cp is not None:
            return self.cp
        
        return 0 # Should not happen
