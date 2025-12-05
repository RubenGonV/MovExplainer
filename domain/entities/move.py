from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Move:
    """
    Entity representing a chess move.
    """
    uci: str
    san: Optional[str] = None

    def __post_init__(self):
        if not self.uci:
            raise ValueError("UCI string cannot be empty")
        # Basic UCI validation (length 4 or 5)
        if len(self.uci) not in (4, 5):
             raise ValueError(f"Invalid UCI move length: {self.uci}")

    def __str__(self):
        return self.san if self.san else self.uci
