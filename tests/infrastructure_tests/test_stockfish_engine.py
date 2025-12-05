"""
Unit and integration tests for the StockfishEngine class.
"""

from unittest.mock import patch, MagicMock
import pytest

from infrastructure.engines.stockfish_engine import StockfishEngine
from domain.entities.evaluation import Evaluation
from domain.value_objects.score import Score
from domain.entities.move import Move


@pytest.mark.unit
class TestStockfishEngineMocked:
    """Unit tests for StockfishEngine using mocks (no real engine)."""

    def test_singleton_pattern(self):
        """Test that StockfishEngine implements Singleton pattern."""
        engine1 = StockfishEngine()
        engine2 = StockfishEngine()

        # Both should be the same instance
        assert engine1 is engine2

    def test_custom_engine_path(self):
        """Test initialization with custom engine path."""
        custom_path = "C:\\custom\\path\\stockfish.exe"
        engine = StockfishEngine(engine_path=custom_path)

        assert engine.engine_path == custom_path

    def test_context_manager_protocol(self):
        """Test that engine supports context manager protocol."""
        engine = StockfishEngine()

        # Should have __enter__ and __exit__ methods
        assert hasattr(engine, "__enter__")
        assert hasattr(engine, "__exit__")

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton state before each test."""
        StockfishEngine.reset_singleton()
        yield
        StockfishEngine.reset_singleton()

    @patch(
        "infrastructure.engines.stockfish_engine.chess.engine.SimpleEngine.popen_uci"
    )
    @patch("infrastructure.engines.stockfish_engine.os.path.isfile")
    def test_evaluate_invalid_fen_raises(self, mock_isfile, _mock_popen):
        """Test that invalid FEN raises ValueError."""
        mock_isfile.return_value = True

        engine = StockfishEngine()

        with pytest.raises(ValueError, match="Invalid FEN"):
            engine.evaluate("invalid fen")

    @patch("infrastructure.engines.stockfish_engine.os.path.isfile")
    def test_engine_not_found_raises(self, mock_isfile):
        """Test that missing engine file raises FileNotFoundError."""
        mock_isfile.return_value = False

        engine = StockfishEngine()

        with pytest.raises(FileNotFoundError, match="Stockfish engine not found"):
            engine.evaluate("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    @patch(
        "infrastructure.engines.stockfish_engine.chess.engine.SimpleEngine.popen_uci"
    )
    @patch("infrastructure.engines.stockfish_engine.os.path.isfile")
    def test_close_is_idempotent(self, mock_isfile, mock_popen):
        """Test that close() can be called multiple times safely."""
        mock_isfile.return_value = True
        mock_engine = MagicMock()
        mock_popen.return_value = mock_engine

        engine = StockfishEngine()

        # Close multiple times should not raise
        engine.close()
        engine.close()
        engine.close()


@pytest.mark.engine
@pytest.mark.integration
class TestStockfishEngineIntegration:
    """Integration tests for StockfishEngine (requires actual Stockfish binary)."""

    @pytest.fixture
    def engine(self):
        """Create an engine instance and clean up after test."""
        engine = StockfishEngine()
        yield engine
        engine.close()

    def test_evaluate_starting_position(self, engine):
        """Test evaluation of starting position."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        evaluation = engine.evaluate(fen, depth=12)

        # Verify return type
        assert isinstance(evaluation, Evaluation)
        assert isinstance(evaluation.score, Score)
        assert evaluation.depth == 12

        # Starting position should be roughly equal (within +/- 50 cp)
        if evaluation.score.cp is not None:
            assert -50 <= evaluation.score.cp <= 50

    def test_evaluate_returns_principal_variation(self, engine):
        """Test that evaluation includes principal variation."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        evaluation = engine.evaluate(fen, depth=12)

        # Should have some PV moves
        assert isinstance(evaluation.pv, list)
        assert len(evaluation.pv) > 0

        # PV moves should be Move objects
        for move in evaluation.pv:
            assert isinstance(move, Move)
            assert move.uci is not None
            assert move.san is not None

    def test_analyze_moves_multiple_candidates(self, engine):
        """Test analyzing multiple candidate moves."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        candidates = ["e2e4", "d2d4", "g1f3"]

        results = engine.analyze_moves(fen, candidates, depth=10)

        # Should return results for all valid moves
        assert isinstance(results, dict)
        assert len(results) == 3

        # Each result should be an Evaluation
        for move_uci, evaluation in results.items():
            assert move_uci in candidates
            assert isinstance(evaluation, Evaluation)
            assert isinstance(evaluation.score, Score)

    def test_analyze_moves_filters_illegal(self, engine):
        """Test that illegal moves are filtered out."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        candidates = ["e2e4", "e2e5", "invalid"]  # e2e5 and invalid are illegal

        results = engine.analyze_moves(fen, candidates, depth=10)

        # Should only have e2e4
        assert len(results) == 1
        assert "e2e4" in results

    def test_evaluate_mate_position(self, engine):
        """Test evaluation of a mate-in-one position."""
        # White to move, mate in 1 with Qh5#
        fen = "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"

        evaluation = engine.evaluate(fen, depth=10)

        # Should detect mate
        assert evaluation.score.mate is not None
        assert evaluation.score.mate > 0  # Positive mate (white wins)

    def test_context_manager_usage(self):
        """Test using engine with context manager."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        with StockfishEngine() as engine:
            evaluation = engine.evaluate(fen, depth=10)
            assert isinstance(evaluation, Evaluation)

        # Engine should be closed after exiting context
        # (We can't easily verify this without accessing internals)

    def test_lazy_initialization(self, engine):
        """Test that engine process starts lazily on first use."""
        # Engine process should not be started yet
        assert not engine.is_engine_running

        # First evaluation should start the process
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        engine.evaluate(fen, depth=10)

        # Now process should be running
        assert engine.is_engine_running

    def test_move_objects_have_san_notation(self, engine):
        """Test that returned Move objects include SAN notation."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        evaluation = engine.evaluate(fen, depth=12)

        # Check PV moves have SAN
        for move in evaluation.pv:
            assert move.san is not None
            assert move.san != move.uci  # SAN should be different from UCI
            # SAN should not contain coordinates (e.g., "e4" not "e2e4")
            assert len(move.san) < len(move.uci) or "x" in move.san or "+" in move.san
