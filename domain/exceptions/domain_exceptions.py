class DomainError(Exception):
    """Base exception for all domain layer errors."""
    pass

class EngineError(DomainError):
    """Raised when there is an error related to the chess engine."""
    pass

class LLMError(DomainError):
    """Raised when there is an error related to the LLM."""
    pass

class InvalidFENError(DomainError):
    """Raised when a FEN string is invalid."""
    pass
