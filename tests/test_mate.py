import os
import sys
import pytest

# Añade la carpeta raíz del proyecto al PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from analysis import evaluate_position


def test_mate_in_one():
    fen = "6k1/5ppp/8/8/8/8/5PPP/Q5K1 w - - 0 1"
    moves = ["a1a8", "g2g3"]

    results = evaluate_position(fen, moves, depth=10)

    assert "a1a8" in results

    mate_eval = results["a1a8"]["mate"]

    assert mate_eval is not None, "El motor debería detectar mate en esta posición"

    print("✔️ Test OK — detectado mate en 1")

def main():
    test_mate_in_one()

if __name__ == "__main__":
    main()