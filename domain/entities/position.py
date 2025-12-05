from dataclasses import dataclass
from domain.value_objects.fen import FEN

@dataclass(frozen=True)
class Position:
    """
    Entity representing a chess board position.
    """
    fen: FEN

    def is_white_turn(self) -> bool:
        """
        Determines if it's white's turn based on the FEN string.
        """
        # FEN structure: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
        # The second field indicates the active color ('w' or 'b')
        parts = self.fen.value.split()
        if len(parts) >= 2:
            return parts[1] == 'w'
        return True # Default to white if unclear, though FEN validation should catch this
