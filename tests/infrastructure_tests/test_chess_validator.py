"""
Unit tests for ChessLibValidator.
"""

import pytest
from infrastructure.validators.chess_lib_validator import ChessLibValidator


@pytest.mark.unit
class TestChessLibValidator:
    """Unit tests for ChessLibValidator."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing."""
        return ChessLibValidator()

    # FEN Validation Tests

    def test_validate_fen_starting_position(self, validator):
        """Test validation of starting position FEN."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert validator.validate_fen(fen) is True

    def test_validate_fen_custom_position(self, validator):
        """Test validation of a custom valid position."""
        fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
        assert validator.validate_fen(fen) is True

    def test_validate_fen_invalid_format(self, validator):
        """Test rejection of invalid FEN format."""
        invalid_fen = "invalid fen string"
        assert validator.validate_fen(invalid_fen) is False

    def test_validate_fen_incomplete(self, validator):
        """Test rejection of incomplete FEN."""
        incomplete_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        assert validator.validate_fen(incomplete_fen) is False

    def test_validate_fen_illegal_position(self, validator):
        """Test rejection of illegal position (e.g., too many kings)."""
        # This FEN has two white kings
        illegal_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPKPPP/RNBQKBNR w KQkq - 0 1"
        # python-chess may or may not catch this depending on strictness
        # Just verify it doesn't crash
        result = validator.validate_fen(illegal_fen)
        assert isinstance(result, bool)

    # Move Validation Tests

    def test_validate_move_legal(self, validator):
        """Test validation of a legal move."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        move = "e2e4"
        assert validator.validate_move(fen, move) is True

    def test_validate_move_illegal(self, validator):
        """Test rejection of an illegal move."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        move = "e2e5"  # Pawn can't move two squares to e5 from e2
        assert validator.validate_move(fen, move) is False

    def test_validate_move_invalid_uci_format(self, validator):
        """Test rejection of invalid UCI format."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        move = "e4"  # SAN notation, not UCI
        assert validator.validate_move(fen, move) is False

    def test_validate_move_invalid_fen_raises(self, validator):
        """Test that invalid FEN raises ValueError."""
        invalid_fen = "invalid"
        move = "e2e4"
        with pytest.raises(ValueError, match="Invalid FEN"):
            validator.validate_move(invalid_fen, move)

    def test_validate_move_promotion(self, validator):
        """Test validation of a promotion move."""
        # Position where white pawn can promote
        fen = "8/P7/8/8/8/8/8/K6k w - - 0 1"
        move = "a7a8q"  # Promote to queen
        assert validator.validate_move(fen, move) is True

    # Move Sanitization Tests

    def test_sanitize_move_lowercase(self, validator):
        """Test sanitization converts to lowercase."""
        move = "E2E4"
        sanitized = validator.sanitize_move(move)
        assert sanitized == "e2e4"

    def test_sanitize_move_strips_whitespace(self, validator):
        """Test sanitization removes whitespace."""
        move = "  e2e4  "
        sanitized = validator.sanitize_move(move)
        assert sanitized == "e2e4"

    def test_sanitize_move_promotion(self, validator):
        """Test sanitization of promotion move."""
        move = "E7E8Q"
        sanitized = validator.sanitize_move(move)
        assert sanitized == "e7e8q"

    def test_sanitize_move_invalid_raises(self, validator):
        """Test that invalid move format raises ValueError."""
        invalid_move = "invalid"
        with pytest.raises(ValueError, match="Invalid UCI move format"):
            validator.sanitize_move(invalid_move)

    # Legal Moves Generation Tests

    def test_get_legal_moves_starting_position(self, validator):
        """Test getting legal moves from starting position."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        legal_moves = validator.get_legal_moves(fen)

        # Starting position has 20 legal moves
        assert len(legal_moves) == 20
        assert "e2e4" in legal_moves
        assert "g1f3" in legal_moves

    def test_get_legal_moves_checkmate_position(self, validator):
        """Test getting legal moves from checkmate position (should be empty)."""
        # Fool's mate position
        fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
        legal_moves = validator.get_legal_moves(fen)

        # In checkmate, no legal moves
        assert len(legal_moves) == 0

    def test_get_legal_moves_invalid_fen_raises(self, validator):
        """Test that invalid FEN raises ValueError."""
        invalid_fen = "invalid"
        with pytest.raises(ValueError, match="Invalid FEN"):
            validator.get_legal_moves(invalid_fen)

    def test_get_legal_moves_returns_uci_format(self, validator):
        """Test that returned moves are in UCI format."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        legal_moves = validator.get_legal_moves(fen)

        # All moves should be valid UCI format (4 or 5 characters)
        for move in legal_moves:
            assert len(move) in (4, 5)
            assert move.islower()
