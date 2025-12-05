"""
Manual verification script for Infrastructure Layer components.
Run this to verify that all infrastructure services are working correctly.
"""

from infrastructure.validators.chess_lib_validator import ChessLibValidator
from infrastructure.llm.prompt_builder import PromptBuilder
from infrastructure.engines.stockfish_engine import StockfishEngine


def test_validator():
    """Test ChessLibValidator."""
    print("=" * 60)
    print("Testing ChessLibValidator")
    print("=" * 60)

    validator = ChessLibValidator()
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    print(f"✓ Valid FEN: {validator.validate_fen(fen)}")
    print(f"✓ Valid move e2e4: {validator.validate_move(fen, 'e2e4')}")
    print(f"✓ Invalid move e2e5: {not validator.validate_move(fen, 'e2e5')}")
    print(f"✓ Legal moves count: {len(validator.get_legal_moves(fen))}")
    print(f"✓ Sanitized 'E2E4': {validator.sanitize_move('E2E4')}")
    print()


def test_prompt_builder():
    """Test PromptBuilder."""
    print("=" * 60)
    print("Testing PromptBuilder")
    print("=" * 60)

    prompt = (
        PromptBuilder()
        .add_position(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            description="starting position",
        )
        .add_move(uci="e2e4", san="e4")
        .add_evaluation(cp=25, depth=15, pv=["e4", "e5", "Nf3"])
        .build()
    )

    print(f"✓ Prompt length: {len(prompt)} chars")
    print(f"✓ Contains 'e4': {'e4' in prompt}")
    print(f"✓ Contains 'chess': {'chess' in prompt.lower()}")
    print("\nSample prompt (first 200 chars):")
    print(prompt[:200] + "...")
    print()


def test_stockfish_engine():
    """Test StockfishEngine."""
    print("=" * 60)
    print("Testing StockfishEngine")
    print("=" * 60)

    engine1 = StockfishEngine()
    engine2 = StockfishEngine()

    print(f"✓ Singleton pattern: {engine1 is engine2}")
    print(f"✓ Engine path configured: {engine1._engine_path is not None}")
    print(f"✓ Context manager support: {hasattr(engine1, '__enter__')}")

    # Test evaluation (requires actual Stockfish binary)
    try:
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        evaluation = engine1.evaluate(fen, depth=10)

        print(f"✓ Evaluation successful")
        print(f"  Score: {evaluation.score}")
        print(f"  Depth: {evaluation.depth}")
        print(f"  PV length: {len(evaluation.pv)}")

        if evaluation.pv:
            print(f"  First move: {evaluation.pv[0]}")

    except FileNotFoundError as e:
        print(f"⚠ Stockfish binary not found (expected for testing): {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    finally:
        engine1.close()

    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Infrastructure Layer Manual Verification")
    print("=" * 60 + "\n")

    test_validator()
    test_prompt_builder()
    test_stockfish_engine()

    print("=" * 60)
    print("Verification Complete!")
    print("=" * 60)
