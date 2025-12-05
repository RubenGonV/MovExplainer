import pytest
from domain.value_objects.fen import FEN
from domain.value_objects.score import Score
from domain.exceptions.domain_exceptions import InvalidFENError

@pytest.mark.unit
def test_fen_validation_valid():
    valid_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    fen = FEN(valid_fen)
    assert fen.value == valid_fen
    assert str(fen) == valid_fen

@pytest.mark.unit
def test_fen_validation_invalid():
    invalid_fen = "invalid fen string"
    with pytest.raises(InvalidFENError):
        FEN(invalid_fen)

@pytest.mark.unit
def test_score_centipawns():
    score = Score(cp=50)
    assert score.to_centipawns() == 50

@pytest.mark.unit
def test_score_mate_positive():
    score = Score(mate=1)
    # Mate in 1 should be close to 10000
    assert score.to_centipawns() == 9999

@pytest.mark.unit
def test_score_mate_negative():
    score = Score(mate=-1)
    # Mate in -1 should be close to -10000
    assert score.to_centipawns() == -9999

@pytest.mark.unit
def test_score_invalid_init():
    with pytest.raises(ValueError):
        Score() # Both None
    
    with pytest.raises(ValueError):
        Score(cp=10, mate=1) # Both set
