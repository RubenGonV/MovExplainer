import re
from dataclasses import dataclass
from domain.exceptions.domain_exceptions import InvalidFENError

@dataclass(frozen=True)
class FEN:
    """
    Value Object representing a Forsyth-Edwards Notation (FEN) string.
    """
    value: str

    def __post_init__(self):
        self._validate()

    def _validate(self):
        """
        Validates the FEN string using a regex.
        """
        # Basic FEN regex validation
        # This is a simplified regex, but covers the structure:
        # Piece placement | Active color | Castling | En passant | Halfmove clock | Fullmove number
        fen_pattern = r"^\s*([rnbqkpRNBQKP1-8]+/){7}[rnbqkpRNBQKP1-8]+\s+[w b]\s+(-|[KQkqA-Ha-h]+)\s+(-|[a-h][36])\s+\d+\s+\d+\s*$"
        
        if not re.match(fen_pattern, self.value):
            raise InvalidFENError(f"Invalid FEN string: {self.value}")

    def __str__(self):
        return self.value
